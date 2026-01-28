package com.gymtracker.model

import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime

@Entity
@Table(name = "workouts")
data class Workout(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    val telegramUserId: Long,
    
    val date: LocalDate = LocalDate.now(),
    
    var notes: String? = null,
    
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "workout_exercises")
data class WorkoutExercise(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workout_id")
    val workout: Workout,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "exercise_id")
    val exercise: Exercise,
    
    val orderIndex: Int = 0,
    
    var notes: String? = null
)

/**
 * Стили плавания для упражнений типа SWIMMING
 */
enum class SwimmingStyle {
    FREESTYLE,   // Кроль
    BREASTSTROKE,// Брасс
    BACKSTROKE,  // На спине
    BUTTERFLY,   // Баттерфляй
    MEDLEY       // Комплекс
}

@Entity
@Table(name = "exercise_sets")
data class ExerciseSet(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workout_exercise_id")
    val workoutExercise: WorkoutExercise,
    
    val setNumber: Int,
    
    // === Поля для силовых упражнений (STRENGTH, WEIGHTED_BODYWEIGHT) ===
    var weight: Double? = null,       // Вес в кг
    var reps: Int? = null,            // Количество повторений
    
    // === Поля для статики и кардио (STATIC, CARDIO_TIME, CARDIO_DISTANCE) ===
    var duration: Int? = null,        // Время в секундах
    var distance: Double? = null,     // Расстояние в метрах
    
    // === Поля для плавания (SWIMMING) ===
    @Enumerated(EnumType.STRING)
    var style: SwimmingStyle? = null, // Стиль плавания
    
    // === Поля для интервальных тренировок (INTERVALS) ===
    var workTime: Int? = null,        // Время работы в секундах
    var restTime: Int? = null,        // Время отдыха в секундах
    
    // === Поля для кардио с уровнем (CARDIO_TIME) ===
    var intensity: Int? = null,       // Уровень интенсивности (1-10 или ватты)
    
    // === Метаданные ===
    var isWarmup: Boolean = false,
    var isToFailure: Boolean = false,
    var notes: String? = null
)

