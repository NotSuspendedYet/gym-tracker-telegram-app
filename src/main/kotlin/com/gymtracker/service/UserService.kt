package com.gymtracker.service

import com.gymtracker.model.User
import com.gymtracker.repository.UserRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class UserService(
    private val userRepository: UserRepository
) {
    
    @Transactional
    fun getOrCreateUser(
        telegramId: Long,
        firstName: String,
        lastName: String? = null,
        username: String? = null,
        photoUrl: String? = null
    ): User {
        val existingUser = userRepository.findByTelegramId(telegramId)
        
        return if (existingUser != null) {
            existingUser.apply {
                this.firstName = firstName
                this.lastName = lastName
                this.username = username
                this.photoUrl = photoUrl
                this.lastActiveAt = LocalDateTime.now()
            }
            userRepository.save(existingUser)
        } else {
            userRepository.save(
                User(
                    telegramId = telegramId,
                    firstName = firstName,
                    lastName = lastName,
                    username = username,
                    photoUrl = photoUrl
                )
            )
        }
    }
    
    fun getUserByTelegramId(telegramId: Long): User? {
        return userRepository.findByTelegramId(telegramId)
    }
}

