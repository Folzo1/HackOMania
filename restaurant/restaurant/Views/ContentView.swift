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
            
            HomeView()
                .tabItem {
                    
                    Label("Home", systemImage: "house")
                    
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
