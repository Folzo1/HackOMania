//
//  RecipeListView.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import SwiftUI

struct RecipeListView: View {
    
    let recipeDetails: [RecipeDetail]
    
    var body: some View {
        
        ScrollView(.vertical, showsIndicators: false) {
            
            VStack (spacing: 16) {
                
                ForEach(recipeDetails) { recipeDetail in
                    
                    NavigationLink(destination: FullRecipeView(recipeDetail:recipeDetail)) {
                        
                        RecipeDetailView(recipeDetail: recipeDetail)
                        
                    }
                    
                }
                
            }
            .padding()
            
        }
        
    }
}
