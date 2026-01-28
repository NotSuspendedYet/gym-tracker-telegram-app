package com.gymtracker.controller

import com.gymtracker.model.*
import com.gymtracker.service.*
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import java.time.LocalDate

data class UserAuthRequest(
    val telegramId: Long,
    val firstName: String,
    val lastName: String? = null,
    val username: String? = null,
    val photoUrl: String? = null
)

data class AddExerciseRequest(
    val workoutId: Long,
    val exerciseId: Long
)

data class AddSetRequest(
    val workoutExerciseId: Long,
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

data class UpdateSetRequest(
    val setId: Long,
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

data class CreateExerciseRequest(
    val name: String,
    val categoryId: Long,
    val userId: Long,
    val exerciseType: String = "STRENGTH"  // По умолчанию силовое
)

data class CategoryDto(
    val id: Long,
    val name: String,
    val icon: String,
    val color: String
)

data class ExerciseDto(
    val id: Long,
    val name: String,
    val categoryId: Long,
    val categoryName: String,
    val exerciseType: String  // STRENGTH, BODYWEIGHT, STATIC, etc.
)

data class WorkoutDto(
    val id: Long,
    val date: LocalDate,
    val exercises: List<WorkoutExerciseDto>
)

data class WorkoutExerciseDto(
    val id: Long,
    val exerciseId: Long,
    val exerciseName: String,
    val categoryName: String,
    val categoryColor: String,
    val exerciseType: String,  // STRENGTH, BODYWEIGHT, STATIC, etc.
    val sets: List<SetDto>
)

data class SetDto(
    val id: Long,
    val setNumber: Int,
    // Силовые
    val weight: Double?,
    val reps: Int?,
    // Статика/Кардио
    val duration: Int?,
    val distance: Double?,
    // Плавание
    val style: String?,
    // Интервалы
    val workTime: Int?,
    val restTime: Int?,
    // Кардио с уровнем
    val intensity: Int?,
    // Метаданные
    val isWarmup: Boolean,
    val isToFailure: Boolean,
    val notes: String?
)

data class ProgressDto(
    val exerciseId: Long,
    val exerciseName: String,
    val data: List<ExerciseProgressPoint>
)

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = ["*"])
class ApiController(
    private val userService: UserService,
    private val workoutService: WorkoutService
) {
    
    @PostMapping("/auth")
    fun authenticate(@RequestBody request: UserAuthRequest): ResponseEntity<User> {
        val user = userService.getOrCreateUser(
            telegramId = request.telegramId,
            firstName = request.firstName,
            lastName = request.lastName,
            username = request.username,
            photoUrl = request.photoUrl
        )
        return ResponseEntity.ok(user)
    }
    
    @GetMapping("/categories")
    fun getCategories(): ResponseEntity<List<CategoryDto>> {
        val categories = workoutService.getCategories().map {
            CategoryDto(it.id, it.name, it.icon, it.color)
        }
        return ResponseEntity.ok(categories)
    }
    
    @GetMapping("/exercises")
    fun getAllExercises(): ResponseEntity<List<ExerciseDto>> {
        val exercises = workoutService.getAllExercises().map {
            ExerciseDto(
                it.id, 
                it.name, 
                it.category.id, 
                it.category.name, 
                it.exerciseType?.name ?: "STRENGTH"  // Default to STRENGTH if null
            )
        }
        return ResponseEntity.ok(exercises)
    }
    
    @GetMapping("/exercises/category/{categoryId}")
    fun getExercisesByCategory(@PathVariable categoryId: Long): ResponseEntity<List<ExerciseDto>> {
        val exercises = workoutService.getExercisesByCategory(categoryId).map {
            ExerciseDto(
                it.id, 
                it.name, 
                it.category.id, 
                it.category.name, 
                it.exerciseType?.name ?: "STRENGTH"  // Default to STRENGTH if null
            )
        }
        return ResponseEntity.ok(exercises)
    }
    
    @GetMapping("/workout/today/{userId}")
    fun getTodayWorkout(@PathVariable userId: Long): ResponseEntity<WorkoutDto> {
        val workout = workoutService.getOrCreateTodayWorkout(userId)
        val workoutDto = buildWorkoutDto(workout)
        return ResponseEntity.ok(workoutDto)
    }
    
    @PostMapping("/workout/exercise")
    fun addExerciseToWorkout(@RequestBody request: AddExerciseRequest): ResponseEntity<WorkoutExerciseDto> {
        val workoutExercise = workoutService.addExerciseToWorkout(request.workoutId, request.exerciseId)
        val dto = buildWorkoutExerciseDto(workoutExercise)
        return ResponseEntity.ok(dto)
    }
    
    @PostMapping("/workout/set")
    fun addSet(@RequestBody request: AddSetRequest): ResponseEntity<SetDto> {
        val set = workoutService.addSetToExercise(
            request.workoutExerciseId,
            SetData(
                setNumber = request.setNumber,
                weight = request.weight,
                reps = request.reps,
                duration = request.duration,
                distance = request.distance,
                style = request.style,
                workTime = request.workTime,
                restTime = request.restTime,
                intensity = request.intensity,
                isWarmup = request.isWarmup,
                isToFailure = request.isToFailure,
                notes = request.notes
            )
        )
        return ResponseEntity.ok(buildSetDto(set))
    }
    
    @PutMapping("/workout/set")
    fun updateSet(@RequestBody request: UpdateSetRequest): ResponseEntity<SetDto> {
        val set = workoutService.updateSet(
            request.setId,
            SetData(
                setNumber = 0, // not used in update
                weight = request.weight,
                reps = request.reps,
                duration = request.duration,
                distance = request.distance,
                style = request.style,
                workTime = request.workTime,
                restTime = request.restTime,
                intensity = request.intensity,
                isWarmup = request.isWarmup,
                isToFailure = request.isToFailure,
                notes = request.notes
            )
        )
        return ResponseEntity.ok(buildSetDto(set))
    }
    
    @DeleteMapping("/workout/set/{setId}")
    fun deleteSet(@PathVariable setId: Long): ResponseEntity<Void> {
        workoutService.deleteSet(setId)
        return ResponseEntity.noContent().build()
    }
    
    @DeleteMapping("/workout/exercise/{workoutExerciseId}")
    fun deleteWorkoutExercise(@PathVariable workoutExerciseId: Long): ResponseEntity<Void> {
        workoutService.deleteWorkoutExercise(workoutExerciseId)
        return ResponseEntity.noContent().build()
    }
    
    @GetMapping("/workouts/{userId}")
    fun getWorkoutHistory(@PathVariable userId: Long): ResponseEntity<List<WorkoutDto>> {
        val workouts = workoutService.getWorkoutHistory(userId).map { buildWorkoutDto(it) }
        return ResponseEntity.ok(workouts)
    }
    
    @GetMapping("/progress/{userId}/{exerciseId}")
    fun getExerciseProgress(
        @PathVariable userId: Long,
        @PathVariable exerciseId: Long
    ): ResponseEntity<ProgressDto> {
        val exercise = workoutService.getExerciseById(exerciseId)
            ?: return ResponseEntity.notFound().build()
        
        val progress = workoutService.getExerciseProgress(userId, exerciseId)
        
        return ResponseEntity.ok(ProgressDto(
            exerciseId = exerciseId,
            exerciseName = exercise.name,
            data = progress
        ))
    }
    
    @PostMapping("/exercises")
    fun createCustomExercise(@RequestBody request: CreateExerciseRequest): ResponseEntity<ExerciseDto> {
        val exerciseType = try {
            ExerciseType.valueOf(request.exerciseType)
        } catch (e: IllegalArgumentException) {
            ExerciseType.STRENGTH
        }
        
        val exercise = workoutService.createCustomExercise(
            request.name, 
            request.categoryId, 
            request.userId,
            exerciseType
        )
        return ResponseEntity.ok(ExerciseDto(
            exercise.id, 
            exercise.name, 
            exercise.category.id, 
            exercise.category.name,
            exercise.exerciseType?.name ?: "STRENGTH"  // Default to STRENGTH if null
        ))
    }
    
    private fun buildWorkoutDto(workout: Workout): WorkoutDto {
        val exercises = workoutService.getWorkoutDetails(workout.id).map { buildWorkoutExerciseDto(it) }
        return WorkoutDto(
            id = workout.id,
            date = workout.date,
            exercises = exercises
        )
    }
    
    private fun buildWorkoutExerciseDto(we: WorkoutExercise): WorkoutExerciseDto {
        val sets = workoutService.getSetsForWorkoutExercise(we.id).map { buildSetDto(it) }
        return WorkoutExerciseDto(
            id = we.id,
            exerciseId = we.exercise.id,
            exerciseName = we.exercise.name,
            categoryName = we.exercise.category.name,
            categoryColor = we.exercise.category.color,
            exerciseType = we.exercise.exerciseType?.name ?: "STRENGTH",  // Default to STRENGTH if null
            sets = sets
        )
    }
    
    private fun buildSetDto(set: ExerciseSet): SetDto {
        return SetDto(
            id = set.id,
            setNumber = set.setNumber,
            weight = set.weight,
            reps = set.reps,
            duration = set.duration,
            distance = set.distance,
            style = set.style?.name,
            workTime = set.workTime,
            restTime = set.restTime,
            intensity = set.intensity,
            isWarmup = set.isWarmup,
            isToFailure = set.isToFailure,
            notes = set.notes
        )
    }
}

