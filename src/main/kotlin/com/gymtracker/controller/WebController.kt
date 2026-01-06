package com.gymtracker.controller

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping

@Controller
class WebController {
    
    @GetMapping("/")
    fun index(): String {
        return "index"
    }
    
    @GetMapping("/app")
    fun app(): String {
        return "app"
    }
}

