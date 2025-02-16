//
//  ContentView.swift
//  restaurant
//
//  Created by Christopher on 15/2/25.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            
            GameView()
                .tabItem {
                    
                    Label("Social", systemImage: "gamecontroller")
                    // use this or use person.2
                    // name it game or name it social
                    
                }
            
            ScanView()
                .tabItem {
                    
                    Label("Scan", systemImage: "barcode.viewfinder")
                    
                }
            
            SavedRecipesView()
                .tabItem {
                    
                    Label("Recipes", systemImage: "list.clipboard")
                    
                }
            
        }
    }
}

#Preview {
    ContentView()
}
