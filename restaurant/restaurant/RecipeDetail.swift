//
//  RecipeDetail.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import Foundation
import SwiftUI

struct RecipeDetail: Identifiable {
    
    let id = UUID()
    let dateReceived: Date
    let recipe: Recipe
    
}

