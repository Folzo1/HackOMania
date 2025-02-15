//
//  Recipe.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import Foundation
import SwiftUI

struct Recipe: Codable, Identifiable {
    
    let id: Int
    let title: String
    let instructions: String
    let matchingIngredients: Int
    let totalIngredients: Int
    let matchPercentage: Double
    let image: String
    
    enum CodingKeys: String, CodingKey {
        
        case id = "recipe_id"
        case title
        case instructions
        case matchingIngredients = "matching_ingredients"
        case totalIngredients = "total_ingredients"
        case matchPercentage = "match_percentage"
        case image
        
    }
}
