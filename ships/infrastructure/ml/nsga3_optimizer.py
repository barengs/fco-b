"""
NSGA-III Genetic Quota Optimizer
Many-objective evolutionary algorithm using reference directions for sustainable fishing quota allocation.
"""

import numpy as np
from platypus import NSGAIII, Problem, Real

class NSGA3QuotaOptimizer:
    """
    Proper NSGA-III implementation for quota optimization using Platypus.
    This optimizer takes LSTM predictions and optimizes them based on multiple objectives.
    """

    def __init__(self, population_size=30, generations=20):
        self.population_size = population_size
        self.generations = generations

    def optimize_lstm_predictions(self, lstm_predictions, historical_catches, environmental_weights=None):
        """
        Optimize LSTM predictions using NSGA-III with multiple objectives:
        1. Maximize total catch potential
        2. Minimize environmental impact
        3. Maximize fairness (equal distribution)
        4. Minimize overfishing risk
        """
        if not lstm_predictions or len(lstm_predictions) == 0:
            return []

        num_ships = len(lstm_predictions)
        if num_ships == 0:
            return []

        lstm_preds = np.array(lstm_predictions)
        hist_catches = np.array(historical_catches) if historical_catches else np.zeros(num_ships)

        if environmental_weights is None:
            environmental_weights = np.ones(num_ships) * 0.1

        def objective_function(vars):
            multipliers = np.array(vars)
            quotas = multipliers * lstm_preds

            # Objective 1: Maximize total catch (minimize negative total)
            total_catch = np.sum(quotas)
            obj1 = -total_catch

            # Objective 2: Minimize environmental impact
            env_impact = np.sum(quotas * environmental_weights)
            obj2 = env_impact

            # Objective 3: Maximize fairness (minimize standard deviation of quotas)
            if len(quotas) > 1:
                fairness = np.std(quotas / (lstm_preds + 1e-8))
            else:
                fairness = 0
            obj3 = fairness

            # Objective 4: Minimize overfishing risk
            hist_avg = np.mean(hist_catches) if len(hist_catches) > 0 else np.mean(lstm_preds)
            overfish_penalty = 0
            for quota in quotas:
                if quota > hist_avg * 1.5:
                    overfish_penalty += (quota - hist_avg * 1.5) * 10
            obj4 = overfish_penalty

            return [obj1, obj2, obj3, obj4]

        problem = Problem(num_ships, 4)
        problem.types[:] = Real(0.1, 2.0)
        problem.function = objective_function

        algorithm = NSGAIII(problem, divisions_outer=3)
        algorithm.run(self.population_size * self.generations)

        if not algorithm.result:
            return [pred * 0.9 for pred in lstm_predictions]

        best_solution = self._select_best_solution(algorithm.result, lstm_preds, hist_catches)
        multipliers = np.array(best_solution.variables)
        optimized_quotas = multipliers * lstm_preds

        return optimized_quotas.tolist()

    def _select_best_solution(self, solutions, lstm_predictions, historical_catches):
        """
        Select the best solution from Pareto front based on balanced criteria
        """
        if not solutions:
            return None

        best_score = float('inf')
        best_solution = solutions[0]

        hist_avg = np.mean(historical_catches) if historical_catches.size > 0 else np.mean(lstm_predictions)

        for solution in solutions:
            multipliers = np.array(solution.variables)
            quotas = multipliers * lstm_predictions

            total_catch = np.sum(quotas)
            env_impact = np.sum(quotas * 0.1)
            fairness = np.std(quotas) if len(quotas) > 1 else 0
            overfish_penalty = sum(max(0, q - hist_avg * 1.3) for q in quotas)

            score = (env_impact * 0.3 + fairness * 0.3 + overfish_penalty * 0.4 - total_catch * 0.1)

            if score < best_score:
                best_score = score
                best_solution = solution

        return best_solution

    def calculate_fitness_scores(self, optimized_predictions, lstm_predictions, historical_catches):
        """
        Calculate fitness scores for optimized predictions based on multiple criteria
        """
        if not optimized_predictions or not lstm_predictions:
            return [0.5] * len(optimized_predictions) if optimized_predictions else []

        fitness_scores = []
        hist_avg = np.mean(historical_catches) if historical_catches else 0

        for opt_pred, lstm_pred in zip(optimized_predictions, lstm_predictions):
            stability_score = 1.0 - min(1.0, abs(opt_pred - lstm_pred) / (lstm_pred + 1e-8))

            if hist_avg > 0:
                sustainability_score = 1.0 - min(1.0, abs(opt_pred - hist_avg) / hist_avg)
            else:
                sustainability_score = 0.8

            env_score = min(1.0, 1000 / (opt_pred + 100))
            fitness = (stability_score * 0.4 + sustainability_score * 0.4 + env_score * 0.2)
            fitness_scores.append(fitness)

        return fitness_scores
