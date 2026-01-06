package com.gymtracker.model

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "users")
data class User(
    @Id
    val telegramId: Long,
    
    var firstName: String,
    
    var lastName: String? = null,
    
    var username: String? = null,
    
    var photoUrl: String? = null,
    
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    var lastActiveAt: LocalDateTime = LocalDateTime.now()
)

