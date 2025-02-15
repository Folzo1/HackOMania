import SwiftUI
import PhotosUI

struct ScanView: View {
    @State private var selectedImages: [PhotosPickerItem] = []
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
                        VStack(alignment: .leading, spacing: 8) {
                            Text(recipe.title)
                                .font(.headline)
                            
                            if let imageURL = recipe.imageURL {
                                AsyncImage(url: URL(string: imageURL)) { image in
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(height: 200)
                                } placeholder: {
                                    ProgressView()
                                }
                            }
                            
                            Text("Match: \(Int(recipe.matchPercentage))%")
                                .font(.subheadline)
                            
                            Text("Instructions:")
                                .font(.subheadline)
                                .padding(.top, 4)
                            
                            Text(recipe.instructions)
                                .font(.body)
                        }
                        .padding(.vertical)
                    }
                }
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

