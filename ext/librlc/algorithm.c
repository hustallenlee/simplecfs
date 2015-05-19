#include "algorithm.h"

int next_permutaion(int *list, int lsize){
    int size = lsize;
    int i, j;
    int temp;

    //stop at the first place where the latter element is greater than the previous element
    for(i = size-1; (i>0)&&(list[i]<list[i-1]); --i);

    if(0 == i) return 0; //at the end of the permutation

    //find first element after list[i-1] greater than it
    for(j = size-1; (j > i)&&(list[j]<list[i-1]); --j);

    temp = list[j];
    list[j] = list[i-1];
    list[i-1] = temp;

    //inverse from list[i] to list[size-1]
    for(j = size-1; i < j; --j, ++i){
        temp = list[i];
        list[i] = list[j];
        list[j] = temp;
    }
    
    return 1;
}
            
int next_combination(int *list, int lsize, int inall){
    int size = lsize;
    int i;
    int value;

    if(list[0] >= (inall-size)){
        return 0;
    }   
    
    for(i = size-1; i > 0; --i){
        if(list[i] < inall-(size-i)){
            break;
        }
    }
    
    value = list[i];
    for(;i < size; ++i){
        ++value;
        list[i] = value;
    }   
    
    return 1;
}
