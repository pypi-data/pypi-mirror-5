# Graf

Graf was built as a daily graph drawing program.
There is a powerfull graph drawing tool called [matplotlib][] but that is too
powerfull and complecated to use as a daily tool.
The purpose of the Graf is to make it easier and simpler for daily graph drawing
powerd by wrapping matplotlib and giving some useful methods for loading or
analysing data.

# Example
Prepare example data in `raw` directory as `data.00.txt`, `data.01.txt`, ...etc.
Save the following code as `example01.graf` and run `graf example01.graf`

```python
# Load column 0 and 1 of data.00.txt, data.01.txt, ... in raw directory
dataset = load('raw/data.??.txt', using=(0, 1))
# Plot all data
for x, y in dataset:
    plot(x, y)
# Show
show()
```

