import SwiftUI
import SpriteKit

struct GameView: View {
    @State private var showSavedRecipes = false
    @State private var scene: GameScene
    
    init() {
        let scene = GameScene()
        scene.size = UIScreen.main.bounds.size
        scene.scaleMode = .fill
        self._scene = State(initialValue: scene)
    }
    
    var body: some View {
        ZStack {
            VStack{
                SpriteView(scene: scene)
                    .frame(width: UIScreen.main.bounds.width, height: UIScreen.main.bounds.height)
                    .ignoresSafeArea()
                    .onAppear {
                        scene.showSavedRecipes = { showSavedRecipes = true }
                    }
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
                Spacer()
          
                
            }
        }
        .sheet(isPresented: $showSavedRecipes, onDismiss: {
            scene.resetCharacterPosition()
        }) {
            SavedRecipesView()
        }
    }
}
