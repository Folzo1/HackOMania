import SwiftUI
import CoreData

struct SavedRecipesView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \SavedRecipe.timestamp, ascending: false)],
        animation: .default)
    private var savedRecipes: FetchedResults<SavedRecipe>

    var body: some View {
        NavigationView {
            List {
                ForEach(savedRecipes) { savedRecipe in
                    NavigationLink(destination: RecipeDetailView(recipe: savedRecipe.toRecipeMatch())) {
                        HStack {
                            if let imageData = savedRecipe.imageData,
                               let uiImage = UIImage(data: imageData) {
                                Image(uiImage: uiImage)
                                    .resizable()
                                    .scaledToFill()
                                    .frame(width: 60, height: 60)
                                    .cornerRadius(8)
                            }
                            
                            VStack(alignment: .leading) {
                                Text(savedRecipe.title ?? "Unknown Recipe")
                                    .font(.headline)
                                Text("\(Int(savedRecipe.matchPercentage))% Match")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                }
                .onDelete(perform: deleteRecipes)
            }
            .navigationTitle("Saved Recipes")
            .toolbar {
                EditButton()
            }
        }
    }
    
    private func deleteRecipes(offsets: IndexSet) {
        offsets.map { savedRecipes[$0] }.forEach(viewContext.delete)
        do {
            try viewContext.save()
        } catch {
            print("Error deleting: \(error)")
        }
    }
}
