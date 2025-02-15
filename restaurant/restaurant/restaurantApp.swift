//
//  RestaurantApp.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import SwiftUI
import Foundation

@main
struct RestaurantApp: App {
    
    let persistence = PersistenceController.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistence.container.viewContext)
        }
    }
}
