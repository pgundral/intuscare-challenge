import pstats
import subprocess

# Run profiling for base_solution.py
subprocess.run(["python3.11", "-m", "cProfile", "-o", "benchmarking/base_solution.prof", "base_solution.py"])

# Run profiling for optimized_solution.py
subprocess.run(["python3.11", "-m", "cProfile", "-o", "benchmarking/optimized_solution.prof", "optimized_solution.py"])

# Run profiling for async_solution.py
subprocess.run(["python3.11", "-m", "cProfile", "-o", "benchmarking/async_solution.prof", "async_solution.py"])
# python3.11 -m cProfile -o optimized_solution.prof optimized_solution.py 
# python3.11 -m cProfile -o async_solution.prof async_solution.py    

p = pstats.Stats("benchmarking/base_solution.prof")
p.strip_dirs().sort_stats("time").print_stats(10)  # Top 10 slowest functions

p = pstats.Stats("benchmarking/optimized_solution.prof")
p.strip_dirs().sort_stats("time").print_stats(10)  # Top 10 slowest functions

p = pstats.Stats("benchmarking/async_solution.prof")
p.strip_dirs().sort_stats("time").print_stats(10)  # Top 10 slowest functions

