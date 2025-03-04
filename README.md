# INTUS CARE CHALLENGE
Pranav Gundrala | Mar 2025

### SOLUTIONS
#### Base Solution
The `base_solution.py` file contains my initial solution for transforming the data. It relies of list comprehension to extract all the patient codes, and then API calls to get descriptions. The solution includes a statement to check if the code has already been defined to reduce API calling.

#### Other Solutions
The `optimized_solution.py` and `async_solution.py` files contain updated solutions that build on the one above. They leverage new techniques to speed up the program. Details below...

`~ 5 hrs`

### BENCHMARKS
The `benchmarking` folder contains `benchmarks.py` which uses cProfiler and pstats to test the efficiency of the above solutions. I wanted to know what parts of my code might be too computationally complex or might otherwise slow down the program if it were to be ran for larger data sets.

`base_solution.py` gave:
```
benchmarking/base_solution.prof

         191628 function calls (186923 primitive calls) in 1.210 seconds

   Ordered by: internal time
   List reduced from 1580 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       11    0.290    0.026    0.290    0.026 {method 'do_handshake' of '_ssl._SSLSocket' objects}
       11    0.269    0.024    0.269    0.024 {method 'read' of '_ssl._SSLSocket' objects}
       11    0.248    0.023    0.248    0.023 {method 'connect' of '_socket.socket' objects}
       11    0.197    0.018    0.197    0.018 {method 'load_verify_locations' of '_ssl._SSLContext' objects}
      129    0.023    0.000    0.023    0.000 {built-in method io.open_code}
    24/21    0.018    0.001    0.019    0.001 {built-in method _imp.create_dynamic}
       11    0.015    0.001    0.017    0.002 connection.py:270(close)
       83    0.013    0.000    0.013    0.000 {built-in method posix.getcwd}
       11    0.011    0.001    0.011    0.001 {built-in method _socket.gethostbyname}
       11    0.010    0.001    0.010    0.001 {built-in method _socket.getaddrinfo}
```

`{method 'do_handshake' of '_ssl.SSLSocket' objects}` and other time intensive processes here are related to the API calling, which appears to be the most rate-limiting step in this program.

In `optimized_solution.py` I attempted to speed up those processes by using `requests.Session()` to open a persistent session, reducing the SLS/TSL handshake bottleneck. This solution also uses the `itertools` package and `map()` to vectorize implementations that would otherwise use for-loops or list comprehension. This is slightly faster. The total runtime and percall times of the most intensive functions were both reduced.

```
185589 function calls (180904 primitive calls) in 0.463 seconds
```

In `async_solution.py` I used the `aiohttp` and `asyncio` packages to set up asynchronous API calling. This allowed the program to make continuous calls without waiting for each one to return the value. Since the ICD-10 API doesn't support batch calling, this is an alternative option to reduce time spent making calls. This reduced total runtime significantly.

```
248342 function calls (240961 primitive calls) in 0.279 seconds
```

**RUN** `benchmarks.py` to see more details.

`~ 1 hr`

### DASHBOARD
I used the `shiny` library in Python to create an interactive webpage that can take an `.json` file input and transform the data using one of two solutions above. The app also uses `cProfile` to display the same metrics described above.

This dashboard was a fun visualization to help show what the programs are doing to the data, but it also acts as a debugging tool. The app is written in the shiny-core syntax, to help separate the UI and Server side code which runs our solutions.

I have experience making visualizations in `shiny` for R, so this was not too time intensive. `~ 3 hrs`
