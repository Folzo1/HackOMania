// NetworkManager.swift
import Foundation

enum NetworkError: Error {
    case invalidData
    case serverError(String)
    case invalidResponse
}

struct RecipeMatch: Codable, Identifiable {
    
    var imageData: Data?
    
    let recipeId: Int
    let title: String
    let instructions: String
    let matchingIngredients: Int
    let totalIngredients: Int
    let matchPercentage: Double
    let imageURL: String?
    var id: Int { recipeId }
    
    enum CodingKeys: String, CodingKey {
        case recipeId = "recipe_id"
        case title
        case instructions
        case matchingIngredients = "matching_ingredients"
        case totalIngredients = "total_ingredients"
        case matchPercentage = "match_percentage"
        case imageURL = "imageURL"
    }
    
}

struct ScanResponse: Codable {
    let matches: [RecipeMatch]
    let logFile: String
    
    enum CodingKeys: String, CodingKey {
        case matches
        case logFile = "log_file"
    }
}

class NetworkManager {
    static let shared = NetworkManager()
    private let baseURL = "http://172.20.10.9:8000"
    
    private init() {}
    
    func uploadImages(_ imageDataArray: [Data], sessionId: String) async throws -> [RecipeMatch] {
        print("Starting upload with \(imageDataArray.count) images")  // Debug print
        let url = URL(string: "\(baseURL)/scan")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var bodyData = Data()
        
        // Add session_id
        bodyData.append("--\(boundary)\r\n".data(using: .utf8)!)
        bodyData.append("Content-Disposition: form-data; name=\"session_id\"\r\n\r\n".data(using: .utf8)!)
        bodyData.append("\(sessionId)\r\n".data(using: .utf8)!)
        
        // Add images
        for (index, imageData) in imageDataArray.enumerated() {
            bodyData.append("--\(boundary)\r\n".data(using: .utf8)!)
            bodyData.append("Content-Disposition: form-data; name=\"images\"; filename=\"image\(index).jpg\"\r\n".data(using: .utf8)!)
            bodyData.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            bodyData.append(imageData)
            bodyData.append("\r\n".data(using: .utf8)!)
        }
        
        bodyData.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = bodyData
        
        let (data, response) = try await URLSession.shared.data(for: request)
        print("Scan response received: \(String(data: data, encoding: .utf8) ?? "none")") // Debug print
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError("Server returned status code \(httpResponse.statusCode)")
        }
        
        // After successful scan, generate recipes
        return try await generateRecipes(sessionId: sessionId)
    }
    
    private func generateRecipes(sessionId: String) async throws -> [RecipeMatch] {
        print("Generating recipes for session: \(sessionId)")  // Debug print
        let url = URL(string: "\(baseURL)/generate_recipe")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["session_id": sessionId]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError("Server returned status code \(httpResponse.statusCode)")
        }
        
        let scanResponse = try JSONDecoder().decode(ScanResponse.self, from: data)
        print("Recipes received: \(scanResponse.matches.count)")  // Debug print
        return scanResponse.matches
    }
}
