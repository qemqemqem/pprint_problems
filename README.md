# pprint_problems

Used to print entries from jsonl files, developed with LLM evals in mind.

## Installation

```pipx install pprint_problems```

## Development

This is still a work in progress. If you have any suggestions or improvements, please feel free to open an issue or a pull request, or contact the author directly.

## Usage

Here are some recommended ways to use this script:

```
See this list of commands and more documentation:
    pprint_problems --help

1. Search for particular problems:
    pprint_problems problems.jsonl -r --search "keyword" -b

2. Load a local file:
    pprint_problems test_problems.jsonl --randomize -n 1 --parts code tests

3. Load a local file with "cat":
    cat problems.jsonl | grep "search_term" | pprint_problems -n 1 -p code

4. Load and randomize problems:
    pprint_problems -r -n 1 problems.jsonl

5. Use some arguments to only load a subset:
    pprint_problems my_problems.jsonl --n 3 --width 100 --line-numbers --randomize

6. Print out the structure:
    pprint_problems --structure test_data.jsonl

7. Print out the raw JSON:
    pprint_problems --n 1 --raw problems.jsonl

8. Manually filter problems with y/n on the keyboard:
    pprint_problems problems.jsonl --manual-filter -p code broken_diff

9. Use the most recently modified file in a directory:
    pprint_problems --dir_most_recent my_jsonl_files/ --structure

10. Graph the distribution of a particular key:
    pprint_problems mydata.jsonl --graph --parts vocab_size

11. Print stats, similarly to graphing:
    pprint_problems mydata.jsonl --stats --parts vocab_size

12. Print the structure, along with stats about the ranges of values:
    pprint_problems mydata.jsonl --structure --ranges
    
13. Print out only parts of a certain type:
    pprint_problems mydata.jsonl --types str numeric bool
```

## Example Usage

### Show the Details of Random Items

Show the `problem["doc_id"]` and `problem["doc"]["question"]` for 3 random items:

```bash
pprint_problems results/samples.jsonl -n 3 -r -p doc_id doc/question
```

```bash
Found 132 problems                                                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 71                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                     doc_id                                      
71                                                                               

                                  doc/question                                   
∀x ∃y {D(n())S(j()),~D(j())T(j())D(f(y,x))} ∃a {D(a*)}                           
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 92                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                     doc_id                                      
92                                                                               

                                  doc/question                                   
{Box(Brown())Box(Yellow())}^{Box(Yellow())}                                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 110                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                     doc_id                                      
110                                                                              

                                  doc/question                                   
∃a ∀x {Q(x*)P(a)} ∀x ∃b {Q(x*)R(b)}^{Q(x*)}         
```

### Searching

Search for items with the word "marble" anywhere in them:

```bash
pprint_problems questions.jsonl -r -n 3 --search marble -p question answers/etr
```

```bash
Found 60 problems                                                                
After searching, found 12 problems                                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 50                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                    question                                     
There is a box in which there is at least a red marble, or else there is a green 
marble and there is a blue marble, but not all three marbles. Is the probability 
of the following situation 33%? There is a green marble and there is a blue      
marble.                                                                          

                                   answers/etr                                   
yes                                                                              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 15                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                    question                                     
There is a box in which there is a grey marble and either a white marble or else 
a mauve marble, but not all three marbles are in the box. Given the preceding    
assertion, is the probability of the following situation 50%? In the box there is
a grey marble and there is a mauve marble.                                       

                                   answers/etr                                   
yes                                                                              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                  Problem 52                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                    question                                     
There is a box in which there is a grey marble, or else a white marble, or else a
mauve marble, but no more than one marble. Given the preceding assertion, is the 
probability of the following situation 0%? In the box there is a grey marble and 
there is a mauve marble.                                                         

                                   answers/etr                                   
yes                                                                              
```

### Showing Parts by Type

Show the string and boolean parts of 1 random item:

```bash
pprint_problems datasets/etr_for_lm_eval.jsonl --types str bool -n 1 -r
```

```bash
Found 4 problems                                                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                   Problem 2                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                    question                                     
Consider the following premises:                                                 

 1 If either voidite is electrically insulating and fluxium is not plasma-like,  
   or fluxium is plasma-like, or voidite is electrically insulating and fluxium  
   is plasma-like, then fluxium is not plasma-like.                              
 2 If aurorium is electrically insulating, then either aurorium is electrically  
   insulating, or aurorium is not electrically insulating.                       

Can you conclude that fluxium is not plasma-like?                                

                   scoring_guide/classically_valid_conclusion                    
true                                                                             

               scoring_guide/question_conclusion_is_etr_conclusion               
false                                                                            
```

### Structure

Here's an example of how to use this program to print out the structure of a dataset:

```bash
pprint_problems questions.jsonl --structure
```

```bash
Found 60 problems                                                                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          JSON Structure (problem 0)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{                                                                                
    "question": str (215 characters)                                             
    "answers": dict (2 items)                                                    
    {                                                                            
        "etr": str (3 characters)                                                
        "classical": str (2 characters)                                          
    }                                                                            
}                                                                              
```

You can also show some details about the contents of the dataset with the `--ranges` flag:

```bash
pprint_problems questions.jsonl --ranges
```

```bash
Found 60 problems                                                                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         JSON Structure (problem 0), with Data Ranges from 60 Samples          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{                                                                                
    "question": str (215 characters) (60 distinct values, length: 38 to 738)     
    "answers": dict (2 items)                                                    
    {                                                                            
        "etr": str (3 characters) (10% no, 90% yes)                              
        "classical": str (2 characters) (63% no, 37% yes)                        
    }                                                                            
}                                                                                
```

## License

This project is licensed under the terms of the MIT license.