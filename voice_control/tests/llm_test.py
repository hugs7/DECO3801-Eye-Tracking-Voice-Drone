from transformers import pipeline
import warnings

from common.logger_helper import init_logger

logger = init_logger()


def main():
    warnings.filterwarnings("ignore")
    # Load a pipeline for text generation using GPT-2
    generator = pipeline("text-generation", model="google/t5-3b")
    command = "Move the drone 50 meters to the right and 20 centimeters left"
    prompt = f"Simplify and shorten the the drone movement into direction and distance example (50m left): {command}"
    result = generator(prompt, max_length=50, num_return_sequences=1)

    logger.info(result[0]["generated_text"])


if __name__ == "__main__":
    main()
