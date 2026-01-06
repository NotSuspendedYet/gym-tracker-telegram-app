package com.gymtracker.service

import com.gymtracker.model.Exercise
import com.gymtracker.model.ExerciseCategory
import com.gymtracker.repository.ExerciseCategoryRepository
import com.gymtracker.repository.ExerciseRepository
import jakarta.annotation.PostConstruct
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class DataInitService(
    private val categoryRepository: ExerciseCategoryRepository,
    private val exerciseRepository: ExerciseRepository
) {
    
    @PostConstruct
    @Transactional
    fun initData() {
        if (categoryRepository.count() > 0) return
        
        // Create categories
        val back = createCategory("Спина", "🔙", "#3b82f6")
        val chest = createCategory("Грудь", "💪", "#ef4444")
        val biceps = createCategory("Бицепс", "💪", "#f97316")
        val triceps = createCategory("Трицепс", "💪", "#eab308")
        val legs = createCategory("Ноги", "🦵", "#22c55e")
        val shoulders = createCategory("Плечи", "🏋️", "#8b5cf6")
        val abs = createCategory("Пресс", "🎯", "#ec4899")
        val cardio = createCategory("Кардио", "🏃", "#06b6d4")
        val other = createCategory("Другое", "⚡", "#6366f1")
        
        // Back exercises
        createExercises(back, listOf(
            "Подтягивания",
            "Подтягивания до груди с облегчением",
            "Высокие подтягивания",
            "Австралийские подтягивания",
            "Тяга горизонтального блока на широчайшую",
            "Тяга вертикального блока узким хватом",
            "Тяга блока сверху широким хватом",
            "Тяга блока сверху узким обратным хватом",
            "Тяга блока сверху-спереди стоя",
            "Тяга блока сидя спереди",
            "Row двумя руками",
            "Row рычажная тяга",
            "Row на трапецию",
            "Тяга гантели в наклоне одной рукой",
            "Тяга гантелей на скамье 45°",
            "Тяга штанги в наклоне",
            "Тяга Т-грифа стоя параллельным хватом",
            "Тяга кроссовера одной рукой горизонтально",
            "Рычажная тяга сверху pull down",
            "Пуловер",
            "Гиперэкстензия"
        ))
        
        // Chest exercises
        createExercises(chest, listOf(
            "Жим гантелей лежа",
            "Жим гантелей на скамье 45° на верх груди",
            "Жим от себя на тренажере",
            "Сведение рук перед собой (бабочка)",
            "Кроссовер сверху",
            "Брусья на грудь",
            "Отжимания узким хватом",
            "Имитация брусьев в тренажере"
        ))
        
        // Biceps exercises
        createExercises(biceps, listOf(
            "Бицепс на тренажере",
            "Подъем штанги на бицепс",
            "Подъем W-штанги на бицепс",
            "Подъем штанги на бицепс обратным хватом",
            "Подъем штанги на брахиалис",
            "Молотки гантелями",
            "Подъем гантелей на бицепс"
        ))
        
        // Triceps exercises
        createExercises(triceps, listOf(
            "Тяга блока сверху на трицепс одной рукой",
            "Тяга блока сверху на трицепс",
            "Французский жим",
            "Обратные отжимания от скамьи",
            "Брусья на трицепс"
        ))
        
        // Legs exercises
        createExercises(legs, listOf(
            "Leg press (жим ногами)",
            "Сгибание ног в тренажере (leg curl)",
            "Разведение ног в стороны в тренажере",
            "Сведение ног в тренажере",
            "Икры на одной ноге с гантелей",
            "Приседания",
            "Выпады"
        ))
        
        // Shoulders exercises
        createExercises(shoulders, listOf(
            "Жим гантелей сидя",
            "Разведение рук на заднюю дельту (бабочка)",
            "Шраги гантелями (трапеция)",
            "Тяга снизу на кроссовере на трапеции",
            "Подъем гантелей перед собой",
            "Махи гантелями в стороны",
            "Шея перед и зад"
        ))
        
        // Abs exercises
        createExercises(abs, listOf(
            "Планка уголок",
            "Пресс берёзка",
            "Русские скручивания",
            "Подъем ног",
            "Подъем корпуса",
            "Скручивания"
        ))
        
        // Cardio exercises
        createExercises(cardio, listOf(
            "Бег",
            "Бассейн",
            "Эллипс",
            "Велотренажер",
            "Скакалка"
        ))
    }
    
    private fun createCategory(name: String, icon: String, color: String): ExerciseCategory {
        return categoryRepository.save(ExerciseCategory(name = name, icon = icon, color = color))
    }
    
    private fun createExercises(category: ExerciseCategory, names: List<String>) {
        names.forEach { name ->
            exerciseRepository.save(
                Exercise(name = name, category = category)
            )
        }
    }
}

