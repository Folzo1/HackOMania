import SwiftUI
import PhotosUI

struct ScanView: View {
    
    @State private var selectedImages: [PhotosPickerItem] = []
    @State private var selectedImageData: [Data] = []
    
    @State private var isPhotosPickerPresented: Bool = false
    @State private var isNewRecipeViewPresented: Bool = false
    @State private var isDocumentScannerPresented: Bool = false
    
    @State var outputImage = OutputImage()
    
    var body: some View {
        
        NavigationStack {
            
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
            
        }
        .navigationTitle("Find Recipes")
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
                    outputImage.imgData = selectedImageData
                    isNewRecipeViewPresented = true
                }
            }
        }
        .fullScreenCover(isPresented: $isNewRecipeViewPresented) {
            NewRecipeView()
        }
        .fullScreenCover(isPresented: $isDocumentScannerPresented) {
            CameraView { images in
                withAnimation(.easeInOut(duration: 0.5)) {
                    isDocumentScannerPresented = false
                    isNewRecipeViewPresented = true
                    
                    // Resize and downsize images
                    outputImage.imgData = images.compactMap { $0.jpegData(compressionQuality: 0.5) }
                }
            }
        }
    }
}

#Preview {
    ScanView()
}
