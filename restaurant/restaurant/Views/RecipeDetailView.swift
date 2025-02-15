
import SwiftUI

struct RecipeDetailView: View {
    let recipe: RecipeMatch
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                if let imageURL = recipe.imageURL {
                    AsyncImage(url: URL(string: imageURL)) { phase in
                        switch phase {
                        case .success(let image):
                            image
                                .resizable()
                                .scaledToFill()
                                .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height / 4)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                                .padding(.horizontal)
                        case .failure:
                            Image(systemName: "photo")
                                .resizable()
                                .scaledToFit()
                                .frame(height: 200)
                        default:
                            ProgressView()
                        }
                    }
                }
                
                VStack(alignment: .leading, spacing: 16) {
                    Text(recipe.title)
                        .font(.largeTitle)
                        .bold()
                        .padding(.top)
                    
                    HStack {
//                        Text("\(Int(recipe.matchPercentage))% Match")
//                            .font(.title3)
//                            .padding(.horizontal)
//                            .padding(.vertical, 8)
//                            .cornerRadius(8)
                        
                        Text("\(recipe.matchingIngredients)/\(recipe.totalIngredients) Ingredients")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Text("Instructions")
                        .font(.title2)
                        .bold()
                        .padding(.top)
                    
                    Text(recipe.instructions)
                        .font(.body)
                }
                .padding()
            }
        }
        .navigationTitle(recipe.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}
