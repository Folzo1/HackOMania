//
//  SavedRecipeExtension.swift
//  restaurant
//
//  Created by Shao Yang Chai on 16/2/25.
//


import SwiftUI
import CoreData

extension SavedRecipe {
    func toRecipeMatch() -> RecipeMatch {
        RecipeMatch(
            imageData: self.imageData ?? Data(),  // New property
            recipeId: Int(self.originalRecipeId),
            title: self.title ?? "",
            instructions: self.instructions ?? "",
            matchingIngredients: Int(self.matchingIngredients),
            totalIngredients: Int(self.totalIngredients),
            matchPercentage: self.matchPercentage,
            imageURL: ""  // Original URL not stored in Core Data
        )
    }
}
