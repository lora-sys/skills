from src.rsi_optimizer import DEFAULT_LR, mean_validation_loss


if __name__ == "__main__":
    for learning_rate in (DEFAULT_LR, 0.2, 1.2):
        print(f"lr={learning_rate:.2f} validation_loss={mean_validation_loss(learning_rate):.6f}")
