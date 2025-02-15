import SwiftUI

struct RecipeCard: View {
    let recipe: RecipeMatch
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Title
            Text(recipe.title)
                .font(.headline)
                .padding(10)
            
            // Image with error handling
            if let url = URL(string: recipe.imageURL!) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                            .frame(maxWidth: .infinity)
                            .frame(height: 150)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                            .padding(.horizontal)
                            
                        
                    case .failure:
                        Image(systemName: "photo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 150)
                            .foregroundColor(.gray)
                    default:
                        ProgressView()
                            .frame(height: 150)
                    }
                }
            }
            
            // Match percentage
            Text("\(Int(recipe.matchPercentage))% Match")
                .font(.subheadline)
                .foregroundColor(.blue)
                .padding(.horizontal)
            
                Text("Instructions:")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
                
                Text(recipe.instructions)
                    .font(.body)
                    .fixedSize(horizontal: false, vertical: false)
                    .lineLimit(5)
                    .padding(.horizontal)
                    .padding(.bottom)
                
        }
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
        .padding(.horizontal)
    }
}
