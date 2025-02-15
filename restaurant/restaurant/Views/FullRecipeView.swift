//
//  FullRecipeView.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import SwiftUI

struct FullRecipeView: View {
    
    let recipeDetail: RecipeDetail
    
    var body: some View {
        
        ScrollView {
            
            VStack(alignment: .leading, spacing: 16) {
                
                AsyncImage(url: URL(string: recipeDetail.recipe.image)) { phase in
                    
                    switch phase {
                        
                    case .empty:
                        ProgressView()
                        
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFit()
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    
                    case.failure:
                        Image(systemName: "house")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 200)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                        let b = print("failed")
                            
                    
                    @unknown default:
                        EmptyView()
                        
                    }
                    
                }
             
                
                Text(recipeDetail.recipe.title)
                    .font(.largeTitle)
                    .bold()
                Text(recipeDetail.recipe.instructions)
                    .font(.body)
                    .padding(.top, 10)
            }
            .padding()
        }
        .navigationTitle(recipeDetail.recipe.title)
    }
}

