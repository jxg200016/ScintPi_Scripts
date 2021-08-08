/* Write and read a binary file (fwrite and fread) */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LEN 50
#define N_STUD 2
#define N_maxSats 100000				/* just works until 100k*/
#define NFREQ       3                   /* number of carrier frequencies */
#define NEXOBS      0                   /* number of extended obs codes */

typedef struct obsd{        /* observation data record      gtime_t time;       /* receiver sampling time (GPST)  */
    int week;               /*4*/
    float tow;              /*4*/
    unsigned char leapseconds;
    unsigned char cons; /* satellite/receiver gnssId */
    unsigned char sat,svid; /* satellite/receiver number */
    signed char elev;        /* elev 1 deg resolution */
    int az;                  /* azimuth 1 deg resolution */
    unsigned char SNR[NFREQ+NEXOBS]; /* signal strength (0.25 dBHz) */
    unsigned char qualL[NFREQ+NEXOBS]; /* quality of carrier phase measurement */
    unsigned char qualP[NFREQ+NEXOBS]; /* quality of pseudorange measurement */
    double L[NFREQ+NEXOBS]; /* observation data carrier-phase (cycle) */
    double P[NFREQ+NEXOBS]; /* observation data pseudorange (m) */
    float flat; /*4*/
    float flon; /*4*/
    float fhei; /*4*/
}obsd_t;
/*C only save lenghts of 2**n */

int findfileSize(char f_n[]) {
   FILE* fp = fopen(f_n, "r"); // opening a file in read mode
   if (fp == NULL) // checking whether the file exists or not
   {
      printf("File Not Found!\n");
      return -1;
   }
   fseek(fp, 0L, SEEK_END);
   int res = ftell(fp); //counting the size of the file
   fclose(fp); //closing the file
   return res;
}

int main( int argc, char *argv[] ) {
   int wtf=0;
   if( argc == 2 ) {
      wtf=1;
      //printf("The argument supplied is %s\n", argv[1]);
   }
   else if( argc > 2 ) {
      printf("Too many arguments supplied.\n");
      return 0;
   }
   else {
      printf("One argument expected.\n");
      return 0;
   }

  FILE *fp;
  obsd_t data0={0};
  obsd_t* ptr; /* Pointer to the array*/
  int i;
  //char f_n[] = {"scintpi3_20210715_1835_967573.3125W_329918.4062N_v325.bin"};
  //int result = findfileSize(f_n);
  int result = findfileSize(argv[1]);
  unsigned int n_sats;
  //obsd_t rawdata[N_maxSats];
  unsigned int nlines = 0;
  char line[1024] = "";
  //if (result != -1) printf("Size of the file is %ld bytes \n", result);
  nlines=result/sizeof(obsd_t);
  printf("%ld \n", sizeof(obsd_t) );

  scanf("%1023s", line);
  // Dynamically allocate memory using malloc()
  ptr = (obsd_t *)malloc((nlines+1)*sizeof(obsd_t));
  for (i=0;i<nlines;i++) ptr[i]=data0; // just to allocate memory
  //printf("memory allocated\n");

  //fp = fopen(f_n, "r"); /* Open the file_name for reading */
  fp = fopen(argv[1],"r");
  if (fp == NULL){
    printf("Error: file.bin cannot be opened\n");
    exit(1);
  }
  //printf("Reading the file? \n");
  /* Read the file */
  n_sats = 0;
  while( fread(&ptr[n_sats], sizeof(obsd_t), 1, fp) == 1 )
  {
    n_sats++;
    //if(n_sats>=nlines) {break;} //n_sats will not over pass nlines
  }
  fclose(fp); /* Close the file */
  /* Print the read records */
  for (i=0; i<(n_sats); i++) {
    printf("%d\t%.2f\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%9.6f\t%9.6f\t%9.6f\t%9.6f\t%f\t%f\t%f\n", ptr[i].week,ptr[i].tow,ptr[i].leapseconds,ptr[i].cons,ptr[i].svid,ptr[i].elev,ptr[i].az,ptr[i].SNR[0],ptr[i].SNR[1],ptr[i].L[0],ptr[i].L[1],ptr[i].P[0],ptr[i].P[1],ptr[i].flat,ptr[i].flon,ptr[i].fhei);
  }
  /*
	  printf("Reading the file? p2 n_sats: %d \n",n_sats);
	  printf("Size of each line is %d bytes \n", sizeof(obsd_t));
	  if (nlines != 0) printf("The number of lines is %d \n", nlines);
  */
  return 0;
}
