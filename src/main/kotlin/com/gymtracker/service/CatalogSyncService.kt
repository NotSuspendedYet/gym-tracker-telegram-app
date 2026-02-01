package com.gymtracker.service

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.gymtracker.model.Exercise
import com.gymtracker.model.ExerciseCategory
import com.gymtracker.model.ExerciseType
import com.gymtracker.repository.ExerciseCategoryRepository
import com.gymtracker.repository.ExerciseRepository
import jakarta.annotation.PostConstruct
import org.slf4j.LoggerFactory
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

/**
 * Сервис синхронизации каталога упражнений.
 * 
 * Читает каталог из JSON файла и синхронизирует с базой данных:
 * - Новые категории/упражнения создаются
 * - Существующие обновляются (переименование работает по catalogId)
 * - Ничего не удаляется (безопасно для данных пользователей)
 */
@Service
class CatalogSyncService(
    private val categoryRepository: ExerciseCategoryRepository,
    private val exerciseRepository: ExerciseRepository,
    private val objectMapper: ObjectMapper
) {
    private val logger = LoggerFactory.getLogger(CatalogSyncService::class.java)
    
    @PostConstruct
    @Transactional
    fun syncCatalog() {
        logger.info("Starting catalog synchronization...")
        
        try {
            // Сначала удаляем дубликаты категорий (от предыдущей миграции)
            cleanupDuplicateCategories()
            
            val catalog = loadCatalog()
            
            val categoriesCreated = syncCategories(catalog.categories)
            val exercisesCreated = syncExercises(catalog.exercises)
            
            logger.info("Catalog sync completed: $categoriesCreated categories, $exercisesCreated exercises added/updated")
        } catch (e: Exception) {
            logger.error("Failed to sync catalog: ${e.message}", e)
        }
    }
    
    /**
     * Удаляет дубликаты категорий, оставляя те у которых есть связанные упражнения.
     */
    private fun cleanupDuplicateCategories() {
        val allCategories = categoryRepository.findAll()
        val byName = allCategories.groupBy { it.name.lowercase() }
        
        for ((name, duplicates) in byName) {
            if (duplicates.size <= 1) continue
            
            logger.info("Found ${duplicates.size} duplicate categories for '$name'")
            
            // Сортируем: сначала те у которых есть упражнения, потом по id (старые первые)
            val sorted = duplicates.sortedWith(
                compareByDescending<ExerciseCategory> { 
                    exerciseRepository.findByCategoryId(it.id).isNotEmpty() 
                }.thenBy { it.id }
            )
            
            val keeper = sorted.first()
            val toDelete = sorted.drop(1)
            
            // Собираем catalogId от дубликатов
            val catalogIdToTransfer = toDelete.firstOrNull { it.catalogId != null }?.catalogId
            
            // Сначала удаляем дубликаты (чтобы освободить catalogId)
            for (dup in toDelete) {
                // Переносим упражнения с дубликата на keeper
                val exercises = exerciseRepository.findByCategoryId(dup.id)
                for (ex in exercises) {
                    ex.category = keeper
                    exerciseRepository.save(ex)
                    logger.debug("Moved exercise '${ex.name}' from category ${dup.id} to ${keeper.id}")
                }
                
                // Удаляем дубликат
                categoryRepository.delete(dup)
                logger.info("Deleted duplicate category: ${dup.id} (${dup.name}), catalogId was: ${dup.catalogId}")
            }
            
            // Теперь присваиваем catalogId keeper'у (после удаления дубликатов)
            if (catalogIdToTransfer != null && keeper.catalogId == null) {
                keeper.catalogId = catalogIdToTransfer
                categoryRepository.save(keeper)
                logger.info("Transferred catalogId '$catalogIdToTransfer' to category ${keeper.id}")
            }
        }
    }
    
    private fun loadCatalog(): Catalog {
        val resource = ClassPathResource("catalog/exercises.json")
        return resource.inputStream.use { stream ->
            objectMapper.readValue(stream)
        }
    }
    
    private fun syncCategories(categories: List<CategoryDto>): Int {
        var count = 0
        
        for (dto in categories) {
            // Сначала ищем по catalogId
            var existing = categoryRepository.findByCatalogId(dto.id)
            
            // Если не найдено по catalogId, ищем по имени (миграция старых данных)
            if (existing == null) {
                existing = categoryRepository.findByNameIgnoreCase(dto.name)
            }
            
            if (existing != null) {
                // Обновляем существующую категорию (+ присваиваем catalogId если его не было)
                var needsUpdate = false
                
                if (existing.catalogId != dto.id) {
                    existing.catalogId = dto.id
                    needsUpdate = true
                }
                if (existing.name != dto.name) {
                    existing.name = dto.name
                    needsUpdate = true
                }
                if (existing.icon != dto.icon) {
                    existing.icon = dto.icon
                    needsUpdate = true
                }
                if (existing.color != dto.color) {
                    existing.color = dto.color
                    needsUpdate = true
                }
                
                if (needsUpdate) {
                    categoryRepository.save(existing)
                    logger.debug("Updated category: ${dto.id} -> ${dto.name}")
                    count++
                }
            } else {
                // Создаём новую категорию
                categoryRepository.save(
                    ExerciseCategory(
                        catalogId = dto.id,
                        name = dto.name,
                        icon = dto.icon,
                        color = dto.color
                    )
                )
                logger.debug("Created category: ${dto.id} -> ${dto.name}")
                count++
            }
        }
        
        return count
    }
    
    private fun syncExercises(exercises: List<ExerciseDto>): Int {
        var count = 0
        
        // Кэшируем категории для быстрого доступа
        val categoryCache = categoryRepository.findAll()
            .filter { it.catalogId != null }
            .associateBy { it.catalogId!! }
        
        for (dto in exercises) {
            val category = categoryCache[dto.category]
            if (category == null) {
                logger.warn("Category not found for exercise ${dto.id}: ${dto.category}")
                continue
            }
            
            val exerciseType = try {
                ExerciseType.valueOf(dto.type)
            } catch (e: Exception) {
                logger.warn("Unknown exercise type for ${dto.id}: ${dto.type}, defaulting to STRENGTH")
                ExerciseType.STRENGTH
            }
            
            val existing = exerciseRepository.findByCatalogId(dto.id)
            
            if (existing != null) {
                // Обновляем существующее упражнение (переименование)
                if (existing.name != dto.name || existing.category.id != category.id || existing.exerciseType != exerciseType) {
                    existing.name = dto.name
                    existing.category = category
                    existing.exerciseType = exerciseType
                    exerciseRepository.save(existing)
                    logger.debug("Updated exercise: ${dto.id} -> ${dto.name}")
                    count++
                }
            } else {
                // Создаём новое упражнение
                exerciseRepository.save(
                    Exercise(
                        catalogId = dto.id,
                        name = dto.name,
                        category = category,
                        exerciseType = exerciseType
                    )
                )
                logger.debug("Created exercise: ${dto.id} -> ${dto.name}")
                count++
            }
        }
        
        return count
    }
    
    // DTO классы для JSON
    data class Catalog(
        val categories: List<CategoryDto>,
        val exercises: List<ExerciseDto>
    )
    
    data class CategoryDto(
        val id: String,
        val name: String,
        val icon: String,
        val color: String
    )
    
    data class ExerciseDto(
        val id: String,
        val category: String,
        val name: String,
        val type: String
    )
}
