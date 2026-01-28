package com.gymtracker.service

import com.gymtracker.model.*
import com.gymtracker.repository.*
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDate

data class SetData(
    val setNumber: Int,
    // Силовые
    val weight: Double? = null,
    val reps: Int? = null,
    // Статика/Кардио
    val duration: Int? = null,
    val distance: Double? = null,
    // Плавание
    val style: String? = null,
    // Интервалы
    val workTime: Int? = null,
    val restTime: Int? = null,
    // Кардио с уровнем
    val intensity: Int? = null,
    // Метаданные
    val isWarmup: Boolean = false,
    val isToFailure: Boolean = false,
    val notes: String? = null
)

data class ExerciseProgressPoint(
    val date: LocalDate,
    val maxWeight: Double?,
    val totalVolume: Double,
    val maxReps: Int?,
    val avgReps: Double?
)

@Service
class WorkoutService(
    private val workoutRepository: WorkoutRepository,
    private val workoutExerciseRepository: WorkoutExerciseRepository,
    private val exerciseSetRepository: ExerciseSetRepository,
    private val exerciseRepository: ExerciseRepository,
    private val exerciseCategoryRepository: ExerciseCategoryRepository
) {
    
    fun getCategories(): List<ExerciseCategory> {
        return exerciseCategoryRepository.findAll()
    }
    
    fun getExercisesByCategory(categoryId: Long): List<Exercise> {
        return exerciseRepository.findByCategoryId(categoryId)
    }
    
    fun getAllExercises(): List<Exercise> {
        return exerciseRepository.findAll()
    }
    
    fun getExerciseById(id: Long): Exercise? {
        return exerciseRepository.findById(id).orElse(null)
    }
    
    @Transactional
    fun getOrCreateTodayWorkout(telegramUserId: Long): Workout {
        val today = LocalDate.now()
        val existingWorkout = workoutRepository.findByTelegramUserIdAndDate(telegramUserId, today)
        
        return existingWorkout ?: workoutRepository.save(
            Workout(telegramUserId = telegramUserId, date = today)
        )
    }
    
    @Transactional
    fun addExerciseToWorkout(workoutId: Long, exerciseId: Long): WorkoutExercise {
        val workout = workoutRepository.findById(workoutId).orElseThrow { 
            IllegalArgumentException("Workout not found") 
        }
        val exercise = exerciseRepository.findById(exerciseId).orElseThrow { 
            IllegalArgumentException("Exercise not found") 
        }
        
        val existingExercises = workoutExerciseRepository.findByWorkoutIdOrderByOrderIndex(workoutId)
        val nextOrder = existingExercises.maxOfOrNull { it.orderIndex }?.plus(1) ?: 0
        
        return workoutExerciseRepository.save(
            WorkoutExercise(
                workout = workout,
                exercise = exercise,
                orderIndex = nextOrder
            )
        )
    }
    
    @Transactional
    fun addSetToExercise(workoutExerciseId: Long, setData: SetData): ExerciseSet {
        val workoutExercise = workoutExerciseRepository.findById(workoutExerciseId).orElseThrow {
            IllegalArgumentException("Workout exercise not found")
        }
        
        // Конвертируем строку стиля в enum
        val swimmingStyle = setData.style?.let { styleName ->
            try {
                SwimmingStyle.valueOf(styleName.uppercase())
            } catch (e: IllegalArgumentException) {
                null
            }
        }
        
        return exerciseSetRepository.save(
            ExerciseSet(
                workoutExercise = workoutExercise,
                setNumber = setData.setNumber,
                weight = setData.weight,
                reps = setData.reps,
                duration = setData.duration,
                distance = setData.distance,
                style = swimmingStyle,
                workTime = setData.workTime,
                restTime = setData.restTime,
                intensity = setData.intensity,
                isWarmup = setData.isWarmup,
                isToFailure = setData.isToFailure,
                notes = setData.notes
            )
        )
    }
    
    @Transactional
    fun updateSet(setId: Long, setData: SetData): ExerciseSet {
        val set = exerciseSetRepository.findById(setId).orElseThrow {
            IllegalArgumentException("Set not found")
        }
        
        // Конвертируем строку стиля в enum
        val swimmingStyle = setData.style?.let { styleName ->
            try {
                SwimmingStyle.valueOf(styleName.uppercase())
            } catch (e: IllegalArgumentException) {
                null
            }
        }
        
        set.apply {
            weight = setData.weight
            reps = setData.reps
            duration = setData.duration
            distance = setData.distance
            style = swimmingStyle
            workTime = setData.workTime
            restTime = setData.restTime
            intensity = setData.intensity
            isWarmup = setData.isWarmup
            isToFailure = setData.isToFailure
            notes = setData.notes
        }
        
        return exerciseSetRepository.save(set)
    }
    
    @Transactional
    fun deleteSet(setId: Long) {
        exerciseSetRepository.deleteById(setId)
    }
    
    @Transactional
    fun deleteWorkoutExercise(workoutExerciseId: Long) {
        val sets = exerciseSetRepository.findByWorkoutExerciseIdOrderBySetNumber(workoutExerciseId)
        exerciseSetRepository.deleteAll(sets)
        workoutExerciseRepository.deleteById(workoutExerciseId)
    }
    
    fun getWorkoutHistory(telegramUserId: Long, limit: Int = 30): List<Workout> {
        return workoutRepository.findByTelegramUserIdOrderByDateDesc(telegramUserId).take(limit)
    }
    
    fun getWorkoutDetails(workoutId: Long): List<WorkoutExercise> {
        return workoutExerciseRepository.findByWorkoutIdOrderByOrderIndex(workoutId)
    }
    
    fun getSetsForWorkoutExercise(workoutExerciseId: Long): List<ExerciseSet> {
        return exerciseSetRepository.findByWorkoutExerciseIdOrderBySetNumber(workoutExerciseId)
    }
    
    fun getExerciseProgress(telegramUserId: Long, exerciseId: Long): List<ExerciseProgressPoint> {
        val sets = exerciseSetRepository.findByUserIdAndExerciseIdOrderByDate(telegramUserId, exerciseId)
        
        // Group by workout date
        val byDate = sets.groupBy { it.workoutExercise.workout.date }
        
        return byDate.map { (date, dateSets) ->
            val weightsWithReps = dateSets.filter { it.weight != null && it.reps != null }
            
            ExerciseProgressPoint(
                date = date,
                maxWeight = dateSets.mapNotNull { it.weight }.maxOrNull(),
                totalVolume = weightsWithReps.sumOf { (it.weight ?: 0.0) * (it.reps ?: 0) },
                maxReps = dateSets.mapNotNull { it.reps }.maxOrNull(),
                avgReps = dateSets.mapNotNull { it.reps }.let { reps ->
                    if (reps.isNotEmpty()) reps.average() else null
                }
            )
        }.sortedBy { it.date }
    }
    
    @Transactional
    fun createCustomExercise(
        name: String, 
        categoryId: Long, 
        userId: Long,
        exerciseType: ExerciseType = ExerciseType.STRENGTH
    ): Exercise {
        val category = exerciseCategoryRepository.findById(categoryId).orElseThrow {
            IllegalArgumentException("Category not found")
        }
        
        return exerciseRepository.save(
            Exercise(
                name = name,
                category = category,
                exerciseType = exerciseType,
                isCustom = true,
                createdByUserId = userId
            )
        )
    }
}

