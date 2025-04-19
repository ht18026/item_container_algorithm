"""
    The program 1 handles the looting aspect of the adventure game Robbie is coding up
"""

from abc import ABC, abstractmethod

class Item:
    """
        The Item class represents an item, with instance attributes name and weight
        The class also has a class attribute known_items to keep track of every Item created
    """
    known_items = []

    def __init__(self, name, weight):
        """
            initialises the class
        """
        self.name = name
        self.weight = weight
        self.known_items.append(self)
        
    def display_info(self):
        """
            displays information of the item
        """
        print(f"{self.name} (weight: {self.weight})")


    

class Container(ABC):
    """
        The Container class represents a container, with instance attributes:
        name
        The class also contains a class attribute available_containers to keep track of every container created
        The container class is an abstract class
    """
    available_containers = []

    def __init__(self, name: str):
        """
            initialises the class
            Input: the name of Container
            Output: None
        """
        
        self.name = name
        # this makes sure names do not overlap in the list of available containers
        if self.name not in [container.name for container in self.available_containers]:
            self.available_containers.append(self)
    
    @abstractmethod
    def loot_item(self, name_of_item: str) -> None:
        """
            loots the item specified and keeps it in the container selected
            Input: the name of the item to be looted
            Output: None
        """
        
        pass
    
    @abstractmethod
    def list_looted_items(self, prefix: str) -> None:
        """
            list the looted items' information
            Input: the prefix is the white space to be added before printing the information
            Output: None
        """

        pass
    
    @abstractmethod
    def get_total_weight(self)-> None:
        """
            get the total weight of this container
            Input: None
            Output: None
        """
        pass
        
class Standard_Container(Container):
    """
        this class represents a standard container, which is the lowest level of containers
    """
    def __init__(self, name: str, empty_weight: float, weight_capacity: float) -> None:
        """
            initialises the Standard_Container class
            Standard containers have an empty weight, a weight capacity,
            an item weight which has the sum of all item weights contained,
            and lastly a list of contained items in this container
            Input: the name of container, the empty weight of container, the capacity of container
            Output: None
        """
        super().__init__(name)
        self.empty_weight = empty_weight
        self.weight_capacity = weight_capacity
        self.contained_items = []
        self.item_weight = 0
    
    def loot_item(self, name_of_item: str) -> None:
        """
            chooses an existing item and attempts to loot the item.
            If the item cannot fit into the container, a failure message will be displayed
            else the item will be put into the container, and the weight will be added.
            Input: the name of the item to be looted
            Output: None
        """
            
        item = get_item_by_name(name_of_item)
        
        # raises an error if the item cannot fit into the current container
        # else loots the item 
        if self.item_weight + item.weight > self.weight_capacity:
            raise ItemNotInContainerError(f"Failure! Item \"{item.name}\" NOT stored in container \"{self.name}\".")
        else:
            self.contained_items.append(item)
            self.item_weight += item.weight
            

    def list_looted_items(self, prefix: str) -> None:
        """
            lists the looted items for this container
            Input: the prefix is the white space to be added before printing the information
            Output: None
        """
        
        print(f"{self.name} (total weight: {self.get_total_weight()}, empty weight: {self.empty_weight}, capacity: {self.item_weight}/{self.weight_capacity})")

        for item in self.contained_items:
            # the prefix here is the indent needed for correct formatting
            print(f"{prefix}   ", end="")
            item.display_info()
    
    def get_total_weight(self) -> float:
        """
            returns the total weight of the container
            Input: None
            Output: the total weight of the container
        """

        return self.empty_weight + self.item_weight
    
    def get_copy(self) -> "Standard_Container":
        """
            returns a new copy of this container
            Input: None
            Output: a copy of this container
        """

        return Standard_Container(self.name, self.empty_weight, self.weight_capacity)

class Multi_Container(Container):
    """
        this class represents a multi container, which can contain multiple containers
    """
    
    def __init__(self, name: str, containers: [str]) -> None:
        """
            initialises a multi_container
            Input: the name of multi_container and a list of container name
            Output: None
        """
        super().__init__(name)
        self.containers = []
        for container_name in containers:
            container = get_container_by_name(container_name)
            
            # gets a new copy of the container if it already exists in the container list
            # this will make each container unique, so that when items are added, the item will
            # only go into one of the containers because they have different references
            if container in self.containers:
                self.containers.append(container.get_copy())
            else:
                self.containers.append(container)


        self.empty_weight = self.get_empty_weight()
    
    def loot_item(self, name_of_item: str) -> None:
        """
            the multi_container version of the loot_item implementation
            Input: the name of item to loot
            Output: None
        """

        # trying every container for looting the item in the order it is added
        # the code that calls this function will handle the ItemNotInContainerError exception accordingly
        for container in self.containers:
        
            try:
                container.loot_item(name_of_item)
                # ends the class method early when it found a match by calling return
                return
            # ignores this exception for every try
            except ItemNotInContainerError:
                continue
                
        # raises error after every container has been tried
        raise ItemNotInContainerError(f"Failure! Item \"{name_of_item}\" NOT stored in container \"{self.name}\".")
    
    def list_looted_items(self, prefix: str) -> None:
        """
            lists the current container's information, then its contained containers' information
            Input: the prefix is the white space to be added before printing the information
            Output: None
        """
        
        print(f"{self.name} (total weight: {self.get_total_weight()}, empty weight: {self.empty_weight}, capacity: 0/0)")
        
        for container in self.containers:
            print("   ", end="")
            # passing 3 spaces to the containers as prefix, so that the contained items are indented correctly
            container.list_looted_items("   ")
    
    def get_empty_weight(self) -> float:
        """
            returns the empty weight of this container
            Input: None
            Output: the empty weight of this container
        """

        empty_weight = 0
        for container in self.containers:
            empty_weight += container.empty_weight
        return empty_weight

    def get_total_weight(self) -> float:
        """ 
            returns the total weight of this container
            Input: None
            Output: the total weight of this container
        """

        # note that the starting total weight is 0 instead of empty weight
        # this is because the total weight of the containers in this container has already
        # added their empty weight into their total weight. And the empty weight of this container
        # is based on the containers in this container
        
        total_weight = 0
        for container in self.containers:
            total_weight += container.get_total_weight()
        return total_weight



class ItemNotInContainerError(Exception):
    """
        this exception is raised when an item cannot be looted into a container
    """

    pass



def read_items() -> None:
    """
        reads items.csv and creates Item objects for each item in the csv
        Input: None
        Output: None
    """
    
    items_csv = read_csv("items.csv")

    for row in items_csv:
        Item(row[0], int(row[1]))


def read_containers() -> None:
    """
        reads containers.csv and creates Container objects for each container in the csv
        Input: None
        Output: None
    """
    
    containers_csv = read_csv("containers.csv")

    for row in containers_csv:
        Standard_Container(row[0], int(row[1]), int(row[2]))


def read_csv(filename: str) -> "Generator":
    """
        creates a generator object for reading csv files
        each item returns a row of the csv, which is a list containing
        items in the row
        Input: filename string 
        Output: A generator for result string
    """
    
    with open(filename, 'r') as f:
        # skips the row containing the column names
        next(f)
        
        for line in f:
            res = line.split(",")
            
            # removes \n character
            res[-1] = res[-1].replace("\n","")
            yield res

def task1_output() -> None:
    """
        prints task1 output with correct formatting for task1
        Input: None
        Output: None 
    """

    print("Items:")
    # items sorted by its name
    for item in sorted(Item.known_items, key=lambda item : item.name):
        print(f"{item.name} (weight: {item.weight})")

    print("\nContainers:")
    # containers sorted by its name
    for container in sorted(Container.available_containers, key=lambda container: container.name):
        print(f"{container.name} (total weight: {container.empty_weight}, empty weight: {container.empty_weight}, capacity: {container.item_weight}/{container.weight_capacity})")
    
    print()


def container_exists(name: str) -> bool:
    """
        checks if the container exists
        Input: the name of container
        Output: if the container exists  
    """
    
    
    names_of_containers = list(map(lambda container : container.name, Container.available_containers))
    return name in names_of_containers

def get_item_by_name(name: str) -> "Item":
    """
        returns the item with the name from the input
        returns None if it doesn't exist
        Input: the name of item
        Output: the item object we find 
    """
    for item in Item.known_items:
        if item.name == name:
            return item
    return None

def get_container_by_name(name: str) -> "Container":
    """
        returns the container with the name from the input
        returns None if it doesn't exist
        Input: the name of the container
        Output: the container object we find 
    """
    
    for container in Container.available_containers:
        if container.name == name:
            return container
    return None



def main():
    """
        the main function for the task
    """

    read_items()
    read_containers()
    print(f"Initialised {len(Item.known_items)+len(Container.available_containers)} items including {len(Container.available_containers)} containers.\n")


    task1_output()

    
main()
