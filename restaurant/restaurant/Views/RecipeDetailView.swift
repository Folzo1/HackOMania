import SwiftUI
import CoreData

struct RecipeDetailView: View {
    let recipe: RecipeMatch
    @State private var isSaved = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                // Image Display
                
                if let imageData = recipe.imageData, let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFill()
                        .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height / 4)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .padding(.horizontal)
                } else if !recipe.imageURL!.isEmpty {
                    AsyncImage(url: URL(string: recipe.imageURL!)) { phase in
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
                } else {
                    Image(systemName: "photo")
                        .resizable()
                        .scaledToFit()
                        .frame(height: 200)
                }
                
                
                VStack(alignment: .leading, spacing: 16) {
                    Text(recipe.title)
                        .font(.largeTitle)
                        .bold()
                        .padding(.top)
                    
                    HStack {
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
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    handleBookmark()
                } label: {
                    Image(systemName: isSaved ? "bookmark.fill" : "bookmark")
                        .foregroundColor(isSaved ? .blue : .primary)
                }
            }
        }
        .alert("Bookmark Status", isPresented: $showingAlert) {
            Button("OK") { }
        } message: {
            Text(alertMessage)
        }
        .onAppear {
            checkSavedStatus()
        }
    }
    private func handleBookmark() {
        if isSaved {
            RecipeDataManager.shared.deleteRecipe(recipe)
            alertMessage = "Recipe removed from bookmarks"
        } else {
            saveRecipeWithImage()
            alertMessage = "Recipe added to bookmarks"
        }
        isSaved.toggle()
        showingAlert = true
    }
    
    private func checkSavedStatus() {
        isSaved = RecipeDataManager.shared.isRecipeSaved(recipe)
    }
    
    private func saveRecipeWithImage() {
        guard let imageURL = URL(string: recipe.imageURL!) else {
            alertMessage = "Error saving image"
            return
        }
        
        URLSession.shared.dataTask(with: imageURL) { data, _, error in
            if let data = data {
                DispatchQueue.main.async {
                    RecipeDataManager.shared.saveRecipe(recipe, imageData: data)
                }
            } else {
                alertMessage = "Failed to download image: \(error?.localizedDescription ?? "Unknown error")"
                showingAlert = true
            }
        }.resume()
    }

}


