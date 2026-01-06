package com.gymtracker

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class GymTrackerApplication

fun main(args: Array<String>) {
    runApplication<GymTrackerApplication>(*args)
}

