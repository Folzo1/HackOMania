//
//  RecipeDetailView.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import SwiftUI

struct RecipeDetailView: View {
    
    let recipeDetail: RecipeDetail
    
    var body: some View {
        
        VStack(alignment: .leading) {
            
            AsyncImage(url: URL(string: recipeDetail.recipe.image)) { phase in
                
                switch phase {
                    
                case .empty:
                    ProgressView()
                    
                    
                    
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFit()
                        .frame(height: 100)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                
                case .failure:
                    Image(systemName: "house")
                        .resizable()
                        .scaledToFit()
                        .frame(height: 100)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                
                @unknown default:
                    EmptyView()
                    
                }
            }
            
            Text(recipeDetail.recipe.title)
                .font(.headline)
                .lineLimit(1)
            
            // date showing
            Text("Received: \(recipeDetail.dateReceived, formatter: dateFormatter) ")
                .font(.subheadline)
                .foregroundStyle(.gray)
            
        }
        .padding()
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .shadow(radius: 5)
        
    }
}

private let dateFormatter: DateFormatter = {
    
    let formatter = DateFormatter()
    formatter.dateStyle = .short
    formatter.timeStyle = .short
    return formatter
    
    
}()
