{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# The Forest Fire Model\n",
    "## A rapid introduction to Mesa\n",
    "\n",
    "The [Forest Fire Model](http://en.wikipedia.org/wiki/Forest-fire_model) is one of the simplest examples of a model that exhibits self-organized criticality.\n",
    "\n",
    "Mesa is a new, Pythonic agent-based modeling framework. A big advantage of using Python is that it a great language for interactive data analysis. Unlike some other ABM frameworks, with Mesa you can write a model, run it, and analyze it all in the same environment. (You don't have to, of course. But you can).\n",
    "\n",
    "In this notebook, we'll go over a rapid-fire (pun intended, sorry) introduction to building and analyzing a model with Mesa."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "First, some imports. We'll go over what all the Mesa ones mean just below."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "ExecuteTime": {
     "end_time": "2024-10-12T18:20:45.476090Z",
     "start_time": "2024-10-12T18:20:45.461936Z"
    }
   },
   "outputs": [
    {
     "ename": "ImportError",
     "evalue": "cannot import name 'BatchRunner' from 'mesa.batchrunner' (/Users/jhkwakkel/Documents/GitHub/mesa/mesa/batchrunner.py)",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mImportError\u001b[0m                               Traceback (most recent call last)",
      "Cell \u001b[0;32mIn[2], line 7\u001b[0m\n\u001b[1;32m      4\u001b[0m get_ipython()\u001b[38;5;241m.\u001b[39mrun_line_magic(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mmatplotlib\u001b[39m\u001b[38;5;124m'\u001b[39m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124minline\u001b[39m\u001b[38;5;124m'\u001b[39m)\n\u001b[1;32m      6\u001b[0m \u001b[38;5;28;01mfrom\u001b[39;00m \u001b[38;5;21;01mmesa\u001b[39;00m \u001b[38;5;28;01mimport\u001b[39;00m Model\n\u001b[0;32m----> 7\u001b[0m \u001b[38;5;28;01mfrom\u001b[39;00m \u001b[38;5;21;01mmesa\u001b[39;00m\u001b[38;5;21;01m.\u001b[39;00m\u001b[38;5;21;01mbatchrunner\u001b[39;00m \u001b[38;5;28;01mimport\u001b[39;00m BatchRunner\n\u001b[1;32m      8\u001b[0m \u001b[38;5;28;01mfrom\u001b[39;00m \u001b[38;5;21;01mmesa\u001b[39;00m\u001b[38;5;21;01m.\u001b[39;00m\u001b[38;5;21;01mdatacollection\u001b[39;00m \u001b[38;5;28;01mimport\u001b[39;00m DataCollector\n",
      "\u001b[0;31mImportError\u001b[0m: cannot import name 'BatchRunner' from 'mesa.batchrunner' (/Users/jhkwakkel/Documents/GitHub/mesa/mesa/batchrunner.py)"
     ]
    }
   ],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "import numpy as np\n",
    "\n",
    "%matplotlib inline\n",
    "\n",
    "from mesa import Model\n",
    "from mesa.batchrunner import BatchRunner\n",
    "from mesa.datacollection import DataCollector"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Building the model\n",
    "\n",
    "Most models consist of basically two things: agents, and an world for the agents to be in. The Forest Fire model has only one kind of agent: a tree. A tree can either be unburned, on fire, or already burned. The environment is a grid, where each cell can either be empty or contain a tree.\n",
    "\n",
    "First, let's define our tree agent. The agent needs to be assigned a cell on the grid, and that's about it. We could assign agents a condition to be in, but for now let's have them all start as being 'Fine'. Since the agent doesn't move, we use `FixedAgent` as the parent class.\n",
    "\n",
    "Next, we define the agent's **step** method. This gets called whenever the agent needs to act in the world. The tree's behavior is simple: If it is currently on fire, it spreads the fire to any neighboring trees that are not burning or have not burned down."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "ExecuteTime": {
     "end_time": "2024-10-12T18:22:50.333734Z",
     "start_time": "2024-10-12T18:22:50.046775Z"
    }
   },
   "outputs": [],
   "source": [
    "from mesa.experimental.cell_space import FixedAgent\n",
    "\n",
    "\n",
    "class TreeCell(FixedAgent):\n",
    "    \"\"\"\n",
    "    A tree cell.\n",
    "\n",
    "    Attributes:\n",
    "        condition: Can be \"Fine\", \"On Fire\", or \"Burned Out\"\n",
    "\n",
    "    \"\"\"\n",
    "\n",
    "    def __init__(self, model, cell):\n",
    "        \"\"\"\n",
    "        Create a new tree.\n",
    "        Args:\n",
    "            model: standard model reference for agent.\n",
    "        \"\"\"\n",
    "        super().__init__(model)\n",
    "        self.condition = \"Fine\"\n",
    "        self.cell = cell\n",
    "\n",
    "    def step(self):\n",
    "        \"\"\"\n",
    "        If the tree is on fire, spread it to fine trees nearby.\n",
    "        \"\"\"\n",
    "        if self.condition == \"On Fire\":\n",
    "            for neighbor in self.cell.neighborhood.agents:\n",
    "                if neighbor.condition == \"Fine\":\n",
    "                    neighbor.condition = \"On Fire\"\n",
    "            self.condition = \"Burned Out\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Now we need to define the model object itself. The main thing the model needs is the grid, which the trees are placed on. We can choose different kinds of grids such as a von Neumann grid where any cell has 4 neighbors (left, right, top and bottom) or Moore grid where a cell has eigh neighbors.\n",
    "\n",
    "The model also needs a few parameters: how large the grid is and what the density of trees on it will be. Density will be the key parameter we'll explore below.\n",
    "\n",
    "Finally, we'll give the model a data collector. This is a Mesa object which collects and stores data on the model as it runs for later analysis.\n",
    "\n",
    "The constructor needs to do a few things. It instantiates all the model-level variables and objects; it randomly places trees on the grid, based on the density parameter; and it starts the fire by setting all the trees on one edge of the grid (x=0) as being On \"Fire\".\n",
    "\n",
    "Next, the model needs a **step** method. Like at the agent level, this method defines what happens every step of the model. We want to activate all the trees, one at a time; then we run the data collector, to count how many trees are currently on fire, burned out, or still fine. If there are no trees left on fire, we stop the model by setting its **running** property to False."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "from mesa.experimental.cell_space import OrthogonalMooreGrid\n",
    "\n",
    "\n",
    "class ForestFire(Model):\n",
    "    \"\"\"\n",
    "    Simple Forest Fire model.\n",
    "    \"\"\"\n",
    "\n",
    "    def __init__(self, width=100, height=100, density=0.65, seed=None):\n",
    "        \"\"\"\n",
    "        Create a new forest fire model.\n",
    "\n",
    "        Args:\n",
    "            width, height: The size of the grid to model\n",
    "            density: What fraction of grid cells have a tree in them.\n",
    "        \"\"\"\n",
    "        super().__init__(seed=seed)\n",
    "\n",
    "        # Set up model objects\n",
    "\n",
    "        self.grid = OrthogonalMooreGrid((width, height), capacity=1)\n",
    "        self.datacollector = DataCollector(\n",
    "            {\n",
    "                \"Fine\": lambda m: self.count_type(m, \"Fine\"),\n",
    "                \"On Fire\": lambda m: self.count_type(m, \"On Fire\"),\n",
    "                \"Burned Out\": lambda m: self.count_type(m, \"Burned Out\"),\n",
    "            }\n",
    "        )\n",
    "\n",
    "        # Place a tree in each cell with Prob = density\n",
    "        for cell in self.grid.all_cells:\n",
    "            if self.random.random() < density:\n",
    "                # Create a tree\n",
    "                new_tree = TreeCell(self, cell)\n",
    "                # Set all trees in the first column on fire.\n",
    "                if cell.coordinate[0] == 0:\n",
    "                    new_tree.condition = \"On Fire\"\n",
    "\n",
    "        self.running = True\n",
    "        self.datacollector.collect(self)\n",
    "\n",
    "    def step(self):\n",
    "        \"\"\"\n",
    "        Advance the model by one step.\n",
    "        \"\"\"\n",
    "        self.agents.shuffle_do(\"step\")\n",
    "        # collect data\n",
    "        self.datacollector.collect(self)\n",
    "\n",
    "        # Halt if no more fire\n",
    "        if self.count_type(self, \"On Fire\") == 0:\n",
    "            self.running = False\n",
    "\n",
    "    @staticmethod\n",
    "    def count_type(model, tree_condition):\n",
    "        \"\"\"\n",
    "        Helper method to count trees in a given condition in a given model.\n",
    "        \"\"\"\n",
    "        return len(model.agents.select(lambda x: x.condition == tree_condition))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Running the model\n",
    "\n",
    "Let's create a model with a 100 x 100 grid, and a tree density of 0.6. Remember, ForestFire takes the arguments *height*, *width*, *density*."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "fire = ForestFire(100, 100, 0.6)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "To run the model until it's done (that is, until it sets its **running** property to False) just use the **run_model()** method. This is implemented in the Model parent object, so we didn't need to implement it above."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "fire.run_model()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "That's all there is to it!\n",
    "\n",
    "But... so what? This code doesn't include a visualization, after all. \n",
    "\n",
    "Remember the data collector? Now we can put the data it collected into a pandas DataFrame:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = fire.dc.get_model_vars_dataframe()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "And chart it, to see the dynamics."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.axes._subplots.AxesSubplot at 0x1819f757a58>"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "results.plot()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "In this case, the fire burned itself out after about 90 steps, with many trees left unburned. \n",
    "\n",
    "You can try changing the density parameter and rerunning the code above, to see how different densities yield different dynamics. For example:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.axes._subplots.AxesSubplot at 0x1819fd724e0>"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "fire = ForestFire(100, 100, 0.8)\n",
    "fire.run_model()\n",
    "results = fire.dc.get_model_vars_dataframe()\n",
    "results.plot()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "... But to really understand how the final outcome varies with density, we can't just tweak the parameter by hand over and over again. We need to do a batch run. \n",
    "\n",
    "## Batch runs\n",
    "\n",
    "Batch runs, also called parameter sweeps, allow use to systemically vary the density parameter, run the model, and check the output. Mesa provides a BatchRunner object which takes a model class, a dictionary of parameters and the range of values they can take and runs the model at each combination of these values. We can also give it reporters, which collect some data on the model at the end of each run and store it, associated with the parameters that produced it.\n",
    "\n",
    "For ease of typing and reading, we'll first create the parameters to vary and the reporter, and then assign them to a new BatchRunner."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "fixed_params = {\"height\": 50, \"width\": 50}  # Height and width are constant\n",
    "# Vary density from 0.01 to 1, in 0.01 increments:\n",
    "variable_params = {\"density\": np.linspace(0, 1, 101)[1:]}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "# At the end of each model run, calculate the fraction of trees which are Burned Out\n",
    "model_reporter = {\n",
    "    \"BurnedOut\": lambda m: (ForestFire.count_type(m, \"Burned Out\") / len(m.agents))\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the batch runner\n",
    "param_run = BatchRunner(\n",
    "    ForestFire,\n",
    "    variable_parameters=variable_params,\n",
    "    fixed_parameters=fixed_params,\n",
    "    model_reporters=model_reporter,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Now the BatchRunner, which we've named param_run, is ready to go. To run the model at every combination of parameters (in this case, every density value), just use the **run_all()** method."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100it [00:04, 11.23it/s]\n"
     ]
    }
   ],
   "source": [
    "param_run.run_all()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Like with the data collector, we can extract the data the batch runner collected into a dataframe:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = param_run.get_model_vars_dataframe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>density</th>\n",
       "      <th>Run</th>\n",
       "      <th>BurnedOut</th>\n",
       "      <th>height</th>\n",
       "      <th>width</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>0.01</td>\n",
       "      <td>0</td>\n",
       "      <td>0.025000</td>\n",
       "      <td>50</td>\n",
       "      <td>50</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>72</th>\n",
       "      <td>0.73</td>\n",
       "      <td>0</td>\n",
       "      <td>0.989983</td>\n",
       "      <td>50</td>\n",
       "      <td>50</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>71</th>\n",
       "      <td>0.72</td>\n",
       "      <td>0</td>\n",
       "      <td>0.992896</td>\n",
       "      <td>50</td>\n",
       "      <td>50</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>70</th>\n",
       "      <td>0.71</td>\n",
       "      <td>0</td>\n",
       "      <td>0.981069</td>\n",
       "      <td>50</td>\n",
       "      <td>50</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>69</th>\n",
       "      <td>0.70</td>\n",
       "      <td>0</td>\n",
       "      <td>0.980057</td>\n",
       "      <td>50</td>\n",
       "      <td>50</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "    density  Run  BurnedOut  height  width\n",
       "0      0.01    0   0.025000      50     50\n",
       "72     0.73    0   0.989983      50     50\n",
       "71     0.72    0   0.992896      50     50\n",
       "70     0.71    0   0.981069      50     50\n",
       "69     0.70    0   0.980057      50     50"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "As you can see, each row here is a run of the model, identified by its parameter values (and given a unique index by the Run column). To view how the BurnedOut fraction varies with density, we can easily just plot them:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(0, 1)"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.scatter(df.density, df.BurnedOut)\n",
    "plt.xlim(0, 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "And we see the very clear emergence of a critical value around 0.5, where the model quickly shifts from almost no trees being burned, to almost all of them.\n",
    "\n",
    "In this case we ran the model only once at each value. However, it's easy to have the BatchRunner execute multiple runs at each parameter combination, in order to generate more statistically reliable results. We do this using the *iteration* argument.\n",
    "\n",
    "Let's run the model 5 times at each parameter point, and export and plot the results as above."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "500it [00:22, 11.33it/s] \n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "(0, 1)"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "param_run = BatchRunner(\n",
    "    ForestFire,\n",
    "    variable_params,\n",
    "    fixed_params,\n",
    "    iterations=5,\n",
    "    model_reporters=model_reporter,\n",
    ")\n",
    "param_run.run_all()\n",
    "df = param_run.get_model_vars_dataframe()\n",
    "plt.scatter(df.density, df.BurnedOut)\n",
    "plt.xlim(0, 1)"
   ]
  }
 ],
 "metadata": {
  "anaconda-cloud": {},
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.6"
  },
  "widgets": {
   "state": {},
   "version": "1.1.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
