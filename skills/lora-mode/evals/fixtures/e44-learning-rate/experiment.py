from src.rsi_optimizer import mean_validation_loss

BASELINE_LR = 0.05
CANDIDATE_LRS = (0.2, 1.2)


if __name__ == "__main__":
    for learning_rate in (BASELINE_LR, *CANDIDATE_LRS):
        print(f"lr={learning_rate:.2f} validation_loss={mean_validation_loss(learning_rate):.6f}")
