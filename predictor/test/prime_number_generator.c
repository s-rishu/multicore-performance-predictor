#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

/***** Globals ******/

int NUM_INPUT = 3;
int N_POS = 1;
int T_POS = 2;

/********************/


/****** Function declarations ******/
// Helper functions
int get_num_digits(int x); /* returns the number of digits in an integer */

// Input/Output functions
void get_input(int argc, char *argv[], int *N, int *t); /* place command-line args into N and t */
int write_output(int N, int *nums); /* write to the N.txt file with formatted info for prime numbers */

// Algorithm functions
void generate_primes(int N, int t, int *nums); /* generate prime numbers based on N and t */
/***********************************/



/*****************************************************************************/
/* returns the number of digits in an integer */
int get_num_digits(int x)
{
	int digits = 0;

	while (x)
	{
		x /= 10;
		++digits;
	}

	return digits;
}


/*****************************************************************************/
/* read inputs from the command-line */
void get_input(int argc, char *argv[], int *N, int *t)
{
	if (argc != NUM_INPUT)
	{
		printf("Invalid number of inputs.\n");
		exit(1);
	}

	*N = atoi(argv[N_POS]);
	*t = atoi(argv[T_POS]);

	if (*N < 2)
	{
		printf("Value for N must be at least 2.\n");
		exit(1);
	}

	if (*t < 1)
	{
		printf("Number of threads, t, cannot be less than 1.\nt will be set to 1.\n");
		*t = 1;
	}
}


/*****************************************************************************/
/* generates prime numbers based on numbers from 2 to N using t threads
 *	1. Generate all #s from 2 to N
 *	2. First # is 2, so remove all #s that are multiples of 2 (i.e. 4, 6, 8, ..., N).
 	   Do not remove 2 itself.
 *	3. Following # is 3, so remove all multiples of 3 that have not been removed
 	   from the previous step. That will be: 9, 15, ..., till you reach N.
 *	4. Next # that has not been crossed so far is 5. So, remove all multiples
 	   of 5 that have not been crossed before, till you reach N.
 *	5. Continue like this till floor((N+1)/2).
 *	6. The remaining #s are the prime numbers.
 */
void generate_primes(int N, int t, int *primes)
{
	#pragma omp parallel num_threads(t)
	{
		// int tid = omp_get_thread_num();
		int nt = omp_get_num_threads();

		int i, j = 0, k = 0;
		int curr_num;
		int local_primes[(N-1)/nt];


		// assign each thread a portion of the numbers from 2, ..., N
		// static scheduling used because finding multiples with larger numbers takes longer than with smaller numbers
		#pragma omp for nowait schedule(static, 1)
		for (i = 2; i <= N; ++i)
		{
			local_primes[j++] = i;
		}
		// NO IMPLICIT BARRIER

		// loop over the elements in local_primes to remove non-prime numbers
		for (i = 0; i < j; ++i)
		{
			curr_num = local_primes[i];

			// check each number in local_primes to see if it is a multiple
			for (k = 2; k <= ((N+1)/2); ++k)
			{
				// current number is a multiple
				if ((curr_num % k) == 0)
				{
					// current number should only be removed if it is a multiple of a smaller number
					if (curr_num != k)
					{
						local_primes[i] = 0;
						break;
					}
				}
				// current number cannot be a multiple of a larger number
				else if (curr_num <= k)
				{
					break;
				}
			}
		}

		// loop over the elements in local_primes
		for (i = 0; i < j; ++i)
		{
			curr_num = local_primes[i];
			// if the current number isn't 0, it is a prime number
			if (curr_num != 0)
			{
				// store local_prime number in the global primes array
				primes[curr_num] = curr_num;
			}
		}

	}


}


/*****************************************************************************/
/* write to the N.txt file with formatted info for prime numbers.
 *	- one prime per line
 *	- each line has the format: a, b, c
 *		- a: the rank of the number (1 means the first prime)
 *		- b: the number itself
 *		- c: the interval from previous prime number (i.e. the current prime - previous prime)
 *	- assume the first line of the file to be: 1, 2, 0
 *	- the second line will then be: 2, 3, 1
 *	- and the third: 3, 5, 2
 *	- and so on...
 */
int write_output(int N, int *nums)
{
	int i;

	// create the output file name as N.txt
	char filename[get_num_digits(N) + 4 + 1]; // "N" + ".txt" + "\0" -> N digits + 4 + 1
	sprintf(filename, "%d.txt", N);

	// open the file in write mode (creates a new file if one doesn't exist)
	FILE *fp = fopen(filename, "w");

	// write to the file in the formatted specified
	int rank = 1;		// the first prime number is always ranked 1
	int prev_num = 2;	// the first prime number is always 2
	int curr_num = 2;	// the first (and current) prime number is always 2

	// loop over 2, ..., N to find the prime numbers
	for (i = 2; i <= N; ++i)
	{
		// if the index does not store a 0, then it is a prime number
		if (nums[i] != 0)
		{
			curr_num = i; // the prime number
			// write the formatted output to the file and post-increment rank
			fprintf(fp, "%d, %d, %d\n", rank++, curr_num, (curr_num - prev_num));
			prev_num = curr_num; // next prime number needs to know the interval
		}
	}

	// close the file
	fclose(fp);

	return 0; // return 0 on success

}

int main(int argc, char *argv[])
{
	/*************************************************************************/

	/* Read input from command-line */
	
	int N, t;

	get_input(argc, argv, &N, &t);



	/* Generate the prime numbers (and do timing) */

	double tstart = 0.0, tend = 0.0, ttaken;

	tstart = omp_get_wtime();
	// START TIMING

	int *primes = (int *) calloc(sizeof(int), (N+1)); // allocate array to store 2, ..., N

	generate_primes(N, t, primes);

	// STOP TIMING
	tend = omp_get_wtime();

	ttaken = tend - tstart;

	printf("Time taken for the main part: %f\n", ttaken);



	/* Write the output file and exit */

	int code = write_output(N, primes);
	if (code != 0) exit(1); // exit with error

	/*************************************************************************/

	free(primes);

	exit(0);
}