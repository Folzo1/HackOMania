//
//  RecipeDataManager.swift
//  restaurant
//
//  Created by Shao Yang Chai on 16/2/25.
//

import CoreData

class RecipeDataManager {
    static let shared = RecipeDataManager()
    private let context = PersistenceController.shared.container.viewContext
    
    func saveRecipe(_ recipe: RecipeMatch, imageData: Data) {
        let newRecipe = SavedRecipe(context: context)
        newRecipe.id = UUID()
        newRecipe.title = recipe.title
        newRecipe.instructions = recipe.instructions
        newRecipe.matchPercentage = recipe.matchPercentage
        newRecipe.imageData = imageData
        newRecipe.timestamp = Date()
        newRecipe.matchingIngredients = Int32(recipe.matchingIngredients)
        newRecipe.totalIngredients = Int32(recipe.totalIngredients)
        newRecipe.originalRecipeId = Int32(recipe.recipeId)
        
        do {
            try context.save()
        } catch {
            print("Error saving recipe: \(error)")
        }
    }
    
    func isRecipeSaved(_ recipe: RecipeMatch) -> Bool {
        let request: NSFetchRequest<SavedRecipe> = SavedRecipe.fetchRequest()
        request.predicate = NSPredicate(format: "title == %@", recipe.title)
        
        do {
            let results = try context.fetch(request)
            return !results.isEmpty
        } catch {
            print("Error checking saved status: \(error)")
            return false
        }
    }
    
    func deleteRecipe(_ recipe: RecipeMatch) {
        let request: NSFetchRequest<SavedRecipe> = SavedRecipe.fetchRequest()
        request.predicate = NSPredicate(format: "title == %@", recipe.title)
        
        do {
            if let result = try context.fetch(request).first {
                context.delete(result)
                try context.save()
            }
        } catch {
            print("Error deleting recipe: \(error)")
        }
    }
    
}

