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
    
    var weight: Double? = null,
    
    var reps: Int? = null,
    
    var duration: Int? = null, // in seconds, for planks etc.
    
    var distance: Double? = null, // in meters, for cardio
    
    var isWarmup: Boolean = false,
    
    var isToFailure: Boolean = false,
    
    var notes: String? = null
)

