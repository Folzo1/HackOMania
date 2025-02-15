import SwiftUI
import PhotosUI

struct ScanView: View {
    
    @State private var selectedImages: [PhotosPickerItem] = []
    
    // final images save to here
    @State private var selectedImageData: [Data] = []
    
    @State private var isPhotosPickerPresented: Bool = false
    @State private var isNewRecipeViewPresented: Bool = false
    @State private var isDocumentScannerPresented: Bool = false
    
    @State private var recipes: [RecipeDetail] = []
    
    @State var outputImage = OutputImage()
    
    var body: some View {
        
        NavigationStack {
            VStack{
                Menu {
                    // by camera
                    Button {
                        isDocumentScannerPresented = true
                    } label: {
                        Image(systemName: "camera.viewfinder")
                        Text("Scan")
                    }
                    // by photos
                    Button {
                        print("Photo Picker")
                        isPhotosPickerPresented = true
                    } label: {
                        Image(systemName: "photo")
                        Text("Photos")
                    }
                } label: {
                    HStack {
                        Image(systemName: "barcode.viewfinder")
                        Text("Scan Barcode")
                    }
                    .bold()
                    .padding()
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .padding()
                
                if !recipes.isEmpty {
                    
                    RecipeListView(recipeDetails: recipes)
                        .padding()
                    
                }
                
                Spacer()
                
            }.navigationTitle("Find Recipes")
        }
        .photosPicker(isPresented: $isPhotosPickerPresented, selection: $selectedImages, maxSelectionCount: 10, matching: .images)

        .onChange(of: selectedImages) { newItems in
            Task {
                var tempImageData: [Data] = []
                
                // Use a task group to load images concurrently
                await withTaskGroup(of: Data?.self) { taskGroup in
                    for newItem in newItems {
                        taskGroup.addTask {
                            // Load image data on a background thread
                            return try? await newItem.loadTransferable(type: Data.self)
                        }
                    }
                    
                    // Collect results from the background tasks
                    for await result in taskGroup {
                        if let data = result {
                            tempImageData.append(data)
                        }
                    }
                }
                
                // Update UI on the main thread
                await MainActor.run {
                    selectedImageData = tempImageData
                    //outputImage.imgData = selectedImageData
                    
                    let newRecipe = RecipeDetail(
                        dateReceived: Date(),
                        recipe: Recipe(
                            id: 13352,
                            title: "Grape and Elderflower Gelée",
                            instructions: "1. Prepare the Gelatin Mixture...",
                            matchingIngredients: 1,
                            totalIngredients: 6,
                            matchPercentage: 16.67,
                            image: "https://images.immediate.co.uk/production/volatile/sites/30/2020/08/chorizo-mozarella-gnocchi-bake-cropped-9ab73a3.jpg?quality=90&webp=true&resize=600,545" // Replace with a valid image URL
                        )
                    )
                    recipes.append(newRecipe)
                    
                }
            }
        }
        .fullScreenCover(isPresented: $isDocumentScannerPresented) {
            CameraView { images in
                withAnimation(.easeInOut(duration: 0.5)) {
                    isDocumentScannerPresented = false
                    
                    // Simulate fetching recipes (replace with actual API call)
                    let newRecipe = RecipeDetail(
                        dateReceived: Date(),
                        recipe: Recipe(
                            id: 13353,
                            title: "Scanned Recipe",
                            instructions: "1. Prepare the ingredients...",
                            matchingIngredients: 3,
                            totalIngredients: 8,
                            matchPercentage: 37.5,
                            image: "https://images.immediate.co.uk/production/volatile/sites/30/2020/08/chorizo-mozarella-gnocchi-bake-cropped-9ab73a3.jpg?quality=90&webp=true&resize=600,545" // Replace with a valid image URL
                        )
                    )
                    recipes.append(newRecipe)
                }
            }
        }
    }
}


#Preview {
    ScanView()
}
