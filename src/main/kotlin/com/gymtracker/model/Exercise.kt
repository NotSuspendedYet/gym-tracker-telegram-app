package com.gymtracker.model

import jakarta.persistence.*

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
    
    val description: String? = null,
    
    val isCustom: Boolean = false,
    
    val createdByUserId: Long? = null
)

