package com.gymtracker.model

import jakarta.persistence.*

/**
 * Типы упражнений, определяющие какие поля доступны для ввода подходов.
 * 
 * STRENGTH - силовые упражнения (вес + повторения): жим, тяга, приседания
 * BODYWEIGHT - упражнения с собственным весом (повторения + опциональный вес для отягощения): 
 *              подтягивания, отжимания, подтягивания с весом
 * STATIC - статические упражнения (только время): планка, вис
 * CARDIO_DISTANCE - кардио с дистанцией (расстояние + время): бег, велосипед
 * CARDIO_TIME - кардио по времени (время + опционально уровень + опционально дистанция): 
 *               эллипс, степпер, гребля
 * SWIMMING - плавание (расстояние + время + стиль): заплывы
 * INTERVALS - интервальные тренировки (время работы + время отдыха + раунды)
 */
enum class ExerciseType {
    STRENGTH,           // вес + повторения
    BODYWEIGHT,         // повторения + опциональный вес (для отягощения)
    STATIC,             // только время
    CARDIO_DISTANCE,    // расстояние + время
    CARDIO_TIME,        // время + опционально уровень + опционально дистанция
    SWIMMING,           // расстояние + время + стиль
    INTERVALS           // работа + отдых + раунды
}

@Entity
@Table(name = "exercise_categories")
data class ExerciseCategory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "catalog_id", unique = true)
    var catalogId: String? = null,  // Уникальный ID из каталога, например "chest"
    
    var name: String,
    
    var icon: String = "💪",
    
    var color: String = "#6366f1"
)

@Entity
@Table(name = "exercises")
data class Exercise(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "catalog_id", unique = true)
    val catalogId: String? = null,  // Уникальный ID из каталога, например "chest_bench_press"
    
    var name: String,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    var category: ExerciseCategory,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "exercise_type")
    var exerciseType: ExerciseType? = ExerciseType.STRENGTH,
    
    val description: String? = null,
    
    val isCustom: Boolean = false,
    
    val createdByUserId: Long? = null
)

