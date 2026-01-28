package com.gymtracker.service

import com.gymtracker.model.Exercise
import com.gymtracker.model.ExerciseCategory
import com.gymtracker.model.ExerciseType
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
        val swimming = createCategory("Плавание", "🏊", "#0ea5e9")
        val other = createCategory("Другое", "⚡", "#6366f1")
        
        // Back exercises (STRENGTH - вес + повторения)
        createExercises(back, ExerciseType.STRENGTH, listOf(
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
            "Пуловер"
        ))
        
        // Back exercises (BODYWEIGHT - только повторения)
        createExercises(back, ExerciseType.BODYWEIGHT, listOf(
            "Подтягивания",
            "Подтягивания до груди с облегчением",
            "Высокие подтягивания",
            "Австралийские подтягивания",
            "Гиперэкстензия"
        ))
        
        // Back exercises (WEIGHTED_BODYWEIGHT - вес + повторения для подтягиваний с отягощением)
        createExercises(back, ExerciseType.WEIGHTED_BODYWEIGHT, listOf(
            "Подтягивания с отягощением"
        ))
        
        // Chest exercises (STRENGTH)
        createExercises(chest, ExerciseType.STRENGTH, listOf(
            "Жим гантелей лежа",
            "Жим гантелей на скамье 45° на верх груди",
            "Жим от себя на тренажере",
            "Сведение рук перед собой (бабочка)",
            "Кроссовер сверху",
            "Имитация брусьев в тренажере"
        ))
        
        // Chest exercises (BODYWEIGHT)
        createExercises(chest, ExerciseType.BODYWEIGHT, listOf(
            "Отжимания",
            "Отжимания узким хватом"
        ))
        
        // Chest exercises (WEIGHTED_BODYWEIGHT)
        createExercises(chest, ExerciseType.WEIGHTED_BODYWEIGHT, listOf(
            "Брусья на грудь",
            "Отжимания с отягощением"
        ))
        
        // Biceps exercises (STRENGTH)
        createExercises(biceps, ExerciseType.STRENGTH, listOf(
            "Бицепс на тренажере",
            "Подъем штанги на бицепс",
            "Подъем W-штанги на бицепс",
            "Подъем штанги на бицепс обратным хватом",
            "Подъем штанги на брахиалис",
            "Молотки гантелями",
            "Подъем гантелей на бицепс"
        ))
        
        // Triceps exercises (STRENGTH)
        createExercises(triceps, ExerciseType.STRENGTH, listOf(
            "Тяга блока сверху на трицепс одной рукой",
            "Тяга блока сверху на трицепс",
            "Французский жим"
        ))
        
        // Triceps exercises (BODYWEIGHT)
        createExercises(triceps, ExerciseType.BODYWEIGHT, listOf(
            "Обратные отжимания от скамьи"
        ))
        
        // Triceps exercises (WEIGHTED_BODYWEIGHT)
        createExercises(triceps, ExerciseType.WEIGHTED_BODYWEIGHT, listOf(
            "Брусья на трицепс"
        ))
        
        // Legs exercises (STRENGTH)
        createExercises(legs, ExerciseType.STRENGTH, listOf(
            "Leg press (жим ногами)",
            "Сгибание ног в тренажере (leg curl)",
            "Разгибание ног в тренажере",
            "Разведение ног в стороны в тренажере",
            "Сведение ног в тренажере",
            "Икры на одной ноге с гантелей",
            "Приседания со штангой",
            "Выпады с гантелями",
            "Румынская тяга"
        ))
        
        // Legs exercises (BODYWEIGHT)
        createExercises(legs, ExerciseType.BODYWEIGHT, listOf(
            "Приседания",
            "Выпады"
        ))
        
        // Shoulders exercises (STRENGTH)
        createExercises(shoulders, ExerciseType.STRENGTH, listOf(
            "Жим гантелей сидя",
            "Разведение рук на заднюю дельту (бабочка)",
            "Шраги гантелями (трапеция)",
            "Тяга снизу на кроссовере на трапеции",
            "Подъем гантелей перед собой",
            "Махи гантелями в стороны",
            "Шея перед и зад",
            "Жим штанги стоя"
        ))
        
        // Abs exercises (STATIC - только время)
        createExercises(abs, ExerciseType.STATIC, listOf(
            "Планка",
            "Планка на боку",
            "Уголок",
            "Вис на турнике"
        ))
        
        // Abs exercises (BODYWEIGHT - только повторения)
        createExercises(abs, ExerciseType.BODYWEIGHT, listOf(
            "Пресс берёзка",
            "Русские скручивания",
            "Подъем ног",
            "Подъем корпуса",
            "Скручивания",
            "Велосипед"
        ))
        
        // Cardio exercises (CARDIO_DISTANCE - расстояние + время)
        createExercises(cardio, ExerciseType.CARDIO_DISTANCE, listOf(
            "Бег на улице",
            "Бег на дорожке",
            "Велосипед",
            "Велотренажер"
        ))
        
        // Cardio exercises (CARDIO_TIME - только время + уровень)
        createExercises(cardio, ExerciseType.CARDIO_TIME, listOf(
            "Эллипс",
            "Степпер",
            "Гребной тренажер"
        ))
        
        // Cardio exercises (INTERVALS - интервальные)
        createExercises(cardio, ExerciseType.INTERVALS, listOf(
            "HIIT",
            "Табата",
            "Интервальный бег"
        ))
        
        // Cardio exercises (BODYWEIGHT)
        createExercises(cardio, ExerciseType.BODYWEIGHT, listOf(
            "Скакалка",
            "Берпи",
            "Jumping jacks"
        ))
        
        // Swimming exercises (SWIMMING - расстояние + время + стиль)
        createExercises(swimming, ExerciseType.SWIMMING, listOf(
            "Кроль",
            "Брасс",
            "Баттерфляй",
            "На спине",
            "Комплексное плавание"
        ))
        
        // Swimming exercises (CARDIO_DISTANCE - просто дистанция заплыва)
        createExercises(swimming, ExerciseType.CARDIO_DISTANCE, listOf(
            "Свободное плавание"
        ))
        
        // Other exercises
        createExercises(other, ExerciseType.STATIC, listOf(
            "Растяжка",
            "Массажный ролл"
        ))
        
        createExercises(other, ExerciseType.BODYWEIGHT, listOf(
            "Разминка"
        ))
    }
    
    private fun createCategory(name: String, icon: String, color: String): ExerciseCategory {
        return categoryRepository.save(ExerciseCategory(name = name, icon = icon, color = color))
    }
    
    private fun createExercises(category: ExerciseCategory, exerciseType: ExerciseType, names: List<String>) {
        names.forEach { name ->
            exerciseRepository.save(
                Exercise(
                    name = name, 
                    category = category, 
                    exerciseType = exerciseType
                )
            )
        }
    }
}

