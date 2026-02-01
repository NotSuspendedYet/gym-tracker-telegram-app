package com.gymtracker.repository

import com.gymtracker.model.*
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDate

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByTelegramId(telegramId: Long): User?
}

@Repository
interface ExerciseCategoryRepository : JpaRepository<ExerciseCategory, Long> {
    fun findByNameIgnoreCase(name: String): ExerciseCategory?
    fun findByCatalogId(catalogId: String): ExerciseCategory?
}

@Repository
interface ExerciseRepository : JpaRepository<Exercise, Long> {
    fun findByCategoryId(categoryId: Long): List<Exercise>
    fun findByNameContainingIgnoreCase(name: String): List<Exercise>
    fun findByIsCustomFalseOrCreatedByUserId(userId: Long): List<Exercise>
    fun findByCatalogId(catalogId: String): Exercise?
}

@Repository
interface WorkoutRepository : JpaRepository<Workout, Long> {
    fun findByTelegramUserIdOrderByDateDesc(telegramUserId: Long): List<Workout>
    fun findByTelegramUserIdAndDate(telegramUserId: Long, date: LocalDate): Workout?
    fun findByTelegramUserIdAndDateBetweenOrderByDateDesc(
        telegramUserId: Long, 
        startDate: LocalDate, 
        endDate: LocalDate
    ): List<Workout>
}

@Repository
interface WorkoutExerciseRepository : JpaRepository<WorkoutExercise, Long> {
    fun findByWorkoutIdOrderByOrderIndex(workoutId: Long): List<WorkoutExercise>
    
    @Query("""
        SELECT we FROM WorkoutExercise we 
        JOIN we.workout w 
        WHERE w.telegramUserId = :userId 
        AND we.exercise.id = :exerciseId 
        ORDER BY w.date DESC
    """)
    fun findByUserIdAndExerciseIdOrderByDateDesc(userId: Long, exerciseId: Long): List<WorkoutExercise>
}

@Repository
interface ExerciseSetRepository : JpaRepository<ExerciseSet, Long> {
    fun findByWorkoutExerciseIdOrderBySetNumber(workoutExerciseId: Long): List<ExerciseSet>
    
    @Query("""
        SELECT es FROM ExerciseSet es 
        JOIN es.workoutExercise we 
        JOIN we.workout w 
        WHERE w.telegramUserId = :userId 
        AND we.exercise.id = :exerciseId 
        ORDER BY w.date ASC, es.setNumber ASC
    """)
    fun findByUserIdAndExerciseIdOrderByDate(userId: Long, exerciseId: Long): List<ExerciseSet>
}

