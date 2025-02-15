import SwiftUI
import PhotosUI

struct ScanView: View {
    @State private var selectedImages: [PhotosPickerItem] = []
    
    // final images save to here
    @State private var selectedImageData: [Data] = []
    @State private var isPhotosPickerPresented: Bool = false
    @State private var isDocumentScannerPresented: Bool = false
    @State private var recipes: [RecipeMatch] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationStack {
            VStack {
                Menu {
                    Button {
                        isDocumentScannerPresented = true
                    } label: {
                        Image(systemName: "camera.viewfinder")
                        Text("Scan")
                    }
                    
                    Button {
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
                
                if isLoading {
                    ProgressView("Processing images...")
                        .padding()
                }
                
                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .padding()
                }
                
                if !recipes.isEmpty {
                    List(recipes, id: \.recipeId) { recipe in
                        NavigationLink(destination: RecipeDetailView(recipe: recipe)) {
                            RecipeCard(recipe: recipe)
                                .frame(height: UIScreen.main.bounds.height / 2.5) // Better height calculation
                                .padding(.vertical, 8)
                        }
                        .listRowBackground(Color.clear) // Clear default background
                        .listRowSeparator(.hidden) // Hide separator
                        .listRowInsets(EdgeInsets(top: 8, leading: 0, bottom: 8, trailing: 0)) // Custom insets
                    }
                    .listStyle(.plain)
                    .scrollContentBackground(.hidden)
                    .background(Color(.systemBackground)) // Ensure proper background
                }
                
                
                Spacer()
                
            }
            .navigationTitle("Find Recipes")
            .photosPicker(isPresented: $isPhotosPickerPresented, selection: $selectedImages, maxSelectionCount: 10, matching: .images)
            .onChange(of: selectedImages) { newItems in
                Task {
                    await processImages(newItems)
                }
            }
            .fullScreenCover(isPresented: $isDocumentScannerPresented) {
                CameraView { images in
                    isDocumentScannerPresented = false
                    Task {
                        await processScannedImages(images)
                    }
                }
            }
        }
    }
    
    private func processImages(_ items: [PhotosPickerItem]) async {
        isLoading = true
        errorMessage = nil
        
        do {
            var imageDataArray: [Data] = []
            
            for item in items {
                if let data = try? await item.loadTransferable(type: Data.self) {
                    imageDataArray.append(data)
                }
            }
            
            let sessionId = UUID().uuidString
            recipes = try await NetworkManager.shared.uploadImages(imageDataArray, sessionId: sessionId)
        } catch {
            errorMessage = "Error: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    private func processScannedImages(_ images: [UIImage]) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let imageDataArray = images.compactMap { image -> Data? in
                return image.jpegData(compressionQuality: 0.8)
            }
            
            let sessionId = UUID().uuidString
            recipes = try await NetworkManager.shared.uploadImages(imageDataArray, sessionId: sessionId)
        } catch {
            errorMessage = "Error: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}

#Preview {
    ScanView()
}

