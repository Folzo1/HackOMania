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
        
        HStack() {
            
            AsyncImage(url: URL(string: recipeDetail.recipe.image)) { phase in
                
                switch phase {
                    
                case .empty:
                    ProgressView()
                    
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFit()
                        .frame(width: 64, height: 48)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                
                case .failure:
                    Image(systemName: "house")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 64, height: 48)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                
                @unknown default:
                    EmptyView()
                    
                }
            }
            VStack(alignment: .leading){
                Text(recipeDetail.recipe.title)
                    .font(.headline)
                
                // date showing
                Text("Received: \(recipeDetail.dateReceived, formatter: dateFormatter) ")
                    .font(.subheadline)
                    .foregroundStyle(.gray)
            }
        }
        .padding()
        .background(Color(.blue))
        .frame(maxWidth: .infinity)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        
    }
}

private let dateFormatter: DateFormatter = {
    
    let formatter = DateFormatter()
    formatter.dateStyle = .short
    formatter.timeStyle = .short
    return formatter
    
    
}()
