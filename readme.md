# ⭐️ Personalized Drama Recommendation System
> **Leveraging Factorization Machines & Embeddings to Enhance Drama Discovery**  
> *A Data-Driven Approach to Personalized Recommendations on MyDramaList (MDL)*  

![PCA Projection](path_to_pca_image.png)  
> *Visualization of user embeddings reduced via PCA, revealing structured user preference clusters.*

## 💭 Motivation (I love dramas!!)
The quality of recommendations in streaming platforms and media discovery systems **solely depends on the richness of user interaction data**. Traditional collaborative filtering approaches **fail in cold-start scenarios** and often **struggle with sparse user-item interactions**.  

This project aligns with **MyDramaList’s mission** of **community-driven drama discovery** by introducing a **deep learning-powered personalized recommendation system**.

### **Why This Matters**
✅ **Brings personalized recommendations to drama lovers** 🎭  
✅ **Enhances community engagement** by surfacing the most relevant dramas  
✅ **Scales efficiently** even when user interactions are sparse  
✅ **Applies Factorization Machines (FM)** to capture complex feature interactions  

---

## 📍 Project Overview
### 1️⃣ Data Collection
We started by **scraping and structuring user interaction data from MyDramaList (MDL)**. The dataset consists of:
- **Users** who have watched, rated, and reviewed dramas  
- **Dramas** with metadata (genres, country, release year, etc.)  
- **User-Drama Interactions** (explicit ratings & implicit feedback)  

### 2️⃣ Preprocessing & Feature Engineering
To build a robust **recommendation model**, we engineered features such as:
- **One-hot encoding of categorical features** (User IDs, Drama IDs)  
- **Latent Embeddings for Users & Dramas**  
- **Sparse matrix representations** for efficient training  
- **Filtering out previously watched dramas** to ensure fresh recommendations  

### 3️⃣ Model Selection: Factorization Machines for Multi-Task Learning
We implemented a **Factorization Machine-based Multi-Task Model**, optimizing for **subrating predictions across multiple categories** (Story, Acting, Cinematography, Enjoyment).  

#### **Model Architecture**
- **Input:** One-hot encoded user-drama pairs  
- **Embedding Layer:** Maps interactions to dense vectors  
- **Factorization Machine (FM) Layer:** Captures feature interactions  
- **Multi-Task Regression Output:** Predicts subratings in range **[1,10]**  

```python
import torch.nn as nn

class FactorizationMachineMultiTask(nn.Module):
    def __init__(self, n_features, k=20, n_outputs=4):
        super().__init__()
        self.linear = nn.Linear(n_features, n_outputs, bias=True)
        self.V = nn.Parameter(torch.randn(n_features, k, n_outputs) * 0.01)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        linear_part = self.linear(x)
        interaction_part = 0.5 * torch.sum(
            torch.pow(torch.matmul(x, self.V), 2) - torch.matmul(torch.pow(x, 2), torch.pow(self.V, 2)), dim=1
        )
        return 1 + 9 * self.sigmoid(output)  # Scale to [1,10]
```

## Preliminary Results and Analysis
PCA Projection of User Embeddings 
![image](https://github.com/user-attachments/assets/67fc63ce-07ba-46f0-876a-0f54fa2f8f9e)

### Example Results 
```
Predicting ratings for Tianqin...
Total dramas to predict: 2055
Top 10 recommended dramas for Tianqin:
1. Mysterious Lotus Casebook - Predicted Rating: 9.37
2. Joy of Life - Predicted Rating: 9.32
3. You Are My Glory - Predicted Rating: 9.30
4. Mr. Queen - Predicted Rating: 9.28
5. Reset - Predicted Rating: 9.27
6. One and Only - Predicted Rating: 9.27
7. Twinkling Watermelon - Predicted Rating: 9.26
8. Eternal Love - Predicted Rating: 9.25
9. Love and Redemption - Predicted Rating: 9.24
10. Reply 1988 - Predicted Rating: 9.24
```


