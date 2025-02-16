//
//  RecipeView1.swift
//  restaurant
//
//  Created by Christopher on 16/2/25.
//

import SwiftUI

struct RecipeView1: View {

    private let placeholderRecipes: [RecipeMatch] = [
        RecipeMatch(imageData: nil, recipeId: 3, title: "Bubble Tea", instructions: """
                    Steps:
                    Cook the tapioca pearls: Bring 4 cups of water to a boil in a pot.
                    Add the tapioca pearls and stir gently. Let them cook for about 15-20 minutes or until they become soft and chewy.
                    Remove from heat, cover, and let them sit for 5 minutes. Drain and rinse under cold water.
                    Make the boba syrup: In a small saucepan, combine 1/4 cup brown sugar and 1/4 cup water.
                    Heat over medium heat until the sugar dissolves and the mixture thickens slightly.
                    Add the cooked tapioca pearls to the syrup and let them soak for 10-15 minutes.Prepare the tea:
                    Brew 1 cup of black tea and let it cool to room temperature.
                    You can chill it in the fridge if needed.Assemble the bubble tea: In a glass, add 2-3 tablespoons of the soaked tapioca pearls.
                    Fill the glass with ice cubes. Pour the cooled black tea over the ice, leaving some room at the top.
                    Add 1/2 cup of milk and 2 tablespoons of sweetened condensed milk or sugar. Stir well to combine.
                    Serve and enjoy: Insert a wide straw into the glass, give it a final stir, and enjoy your homemade bubble tea!
                    """, matchingIngredients: 5, totalIngredients: 5, matchPercentage: 100, imageURL: "https://assets.epicurious.com/photos/5953ca064919e41593325d97/4:3/w_4992,h_3744,c_limit/bubble_tea_recipe_062817.jpg")
    ]
    
    var body: some View {
        NavigationStack {
            List(placeholderRecipes, id: \.recipeId) { recipe in
                NavigationLink(destination: RecipeDetailView(recipe: recipe)) {
                    RecipeCard(recipe: recipe)
                        .frame(height: UIScreen.main.bounds.height / 2.5)
                        .padding(.vertical, 8)
                }
                .listRowBackground(Color.clear)
                .listRowSeparator(.hidden)
                .listRowInsets(EdgeInsets(top: 8, leading: 0, bottom: 8, trailing: 0))
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
            .background(Color(.systemBackground))
            .navigationTitle("Chris's Recipes")
        }
    }
}

#Preview {
    RecipeView1()
}
