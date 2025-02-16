//
//  RecipeView1.swift
//  restaurant
//
//  Created by Christopher on 16/2/25.
//

import SwiftUI

struct RecipeView2: View {

    private let placeholderRecipes: [RecipeMatch] = [
        RecipeMatch(imageData: nil, recipeId: 3, title: "Pizza", instructions: """
                    Steps:
                    Make the dough: In a large bowl, dissolve the yeast and sugar in warm water. Let it sit for 5-10 minutes until frothy. Add the olive oil, salt, and 3 1/2 cups of flour. Mix until a dough forms. Knead on a floured surface for 5-7 minutes, adding more flour if needed, until the dough is smooth and elastic. Place the dough in a greased bowl, cover with a damp cloth, and let it rise for 1-2 hours or until doubled in size.
                    Preheat the oven: Preheat your oven to 475°F (245°C). If you have a pizza stone, place it in the oven to heat up.
                    Prepare the pizza: Punch down the dough and divide it into two portions if making two pizzas. Roll out the dough on a floured surface into your desired shape and thickness. Transfer the dough to a pizza peel or baking sheet lined with parchment paper.
                    Add toppings: Spread a thin layer of pizza sauce over the dough, leaving a small border around the edges. Sprinkle shredded mozzarella cheese evenly over the sauce. Add your favorite toppings. Drizzle a little olive oil over the top for extra flavor.
                    Bake the pizza: Carefully transfer the pizza to the preheated oven (or onto the pizza stone if using). Bake for 10-15 minutes, or until the crust is golden and the cheese is bubbly and slightly browned.
                    Finish and serve: Remove the pizza from the oven and let it cool for a few minutes. Sprinkle with grated Parmesan, red pepper flakes, or fresh basil if desired. Slice and enjoy!
                    """, matchingIngredients: 5, totalIngredients: 5, matchPercentage: 100, imageURL: "https://www.foodandwine.com/thmb/Wd4lBRZz3X_8qBr69UOu2m7I2iw=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/classic-cheese-pizza-FT-RECIPE0422-31a2c938fc2546c9a07b7011658cfd05.jpg")
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
            .navigationTitle("Shao Yang's Recipes")
        }
    }
}

#Preview {
    RecipeView2()
}
