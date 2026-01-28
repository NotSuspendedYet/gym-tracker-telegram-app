package com.gymtracker.model

import jakarta.persistence.*

/**
 * Типы упражнений, определяющие какие поля доступны для ввода подходов.
 * 
 * STRENGTH - силовые упражнения (вес + повторения): жим, тяга, приседания
 * BODYWEIGHT - упражнения с собственным весом (только повторения): отжимания, подтягивания
 * WEIGHTED_BODYWEIGHT - с собственным весом + отягощение (вес + повторения): подтягивания с весом
 * STATIC - статические упражнения (только время): планка, вис
 * CARDIO_DISTANCE - кардио с дистанцией (расстояние + время): бег, велосипед
 * CARDIO_TIME - кардио по времени (время + опционально уровень): эллипс, степпер
 * SWIMMING - плавание (расстояние + время + стиль): заплывы
 * INTERVALS - интервальные тренировки (время работы + время отдыха + раунды)
 */
enum class ExerciseType {
    STRENGTH,           // вес + повторения
    BODYWEIGHT,         // только повторения
    WEIGHTED_BODYWEIGHT,// вес + повторения (подтягивания с весом)
    STATIC,             // только время
    CARDIO_DISTANCE,    // расстояние + время
    CARDIO_TIME,        // только время (+ опционально уровень)
    SWIMMING,           // расстояние + время + стиль
    INTERVALS           // работа + отдых + раунды
}

@Entity
@Table(name = "exercise_categories")
data class ExerciseCategory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    val name: String,
    
    val icon: String = "💪",
    
    val color: String = "#6366f1"
)

@Entity
@Table(name = "exercises")
data class Exercise(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    val name: String,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    val category: ExerciseCategory,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "exercise_type")
    val exerciseType: ExerciseType? = ExerciseType.STRENGTH,
    
    val description: String? = null,
    
    val isCustom: Boolean = false,
    
    val createdByUserId: Long? = null
)

