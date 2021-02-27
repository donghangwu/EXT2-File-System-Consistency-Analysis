#!/usr/bin/env python3

#NAME:Donghang Wu, Tristan Que
#ID: 605346965, 505379744
#EMAIL: dwu20@g.ucla.edu, tristanq816@gmail.com
import sys,csv

#data structures varaibles:
superBlock=None
group=None
inodes=[]
in_dirs=[]
ifree=[]
bfree=[]
fail=False
#define data structures:
class Super:
    def __init__(self,data):
        self.blocks_count = int(data[1])     #total number of blocks
        self.inodes_count = int(data[2])     #total number of inodes
        self.bsize =        int(data[3])              #block size
        self.inode_size =   int(data[4])       #size of inode structure
        self.blocks_per_group = int(data[5])    #blocks per group
        self.inodes_per_group = int(data[6])    #inodes per group
        self.first_ino =        int(data[7])        #first non reserved inode

class Group:
    def __init__(self,data):
        self.group_num =    int(data[1])
        self.blocks_count = int(data[2]) #redundant info
        self.inodes_count = int(data[3]) #redundant info
        self.bfree_count =  int(data[4]) #num of bfree
        self.ifree_count =  int(data[5]) #num of ifree
        self.block_bitmap = int(data[6]) #starting block# for free block entries
        self.inode_bitmap = int(data[7]) #starting block# for free node entries
        self.inode_table =  int(data[8]) #starting block# for first block of inodes

class Inode:
    def __init__(self,data):
        self.node_num=int(data[1])
        self.file_type=data[2]
        self.i_mode	=int(data[3])   #/* File mode */
        self.i_uid=    int(data[4]) #Uid
        self.i_gid	=int(data[5])	#* Group Id *#
        self.i_links_count=int(data[6])	#* Links count *#
        
        self.i_atime=(data[9])	#* Access time *#
        self.i_ctime=(data[7])	#* Creation time *#
        self.i_mtime=(data[8])	#* Modification time *#

        self.i_size	=int(data[10])	#* Size in bytes *#
        
        self.i_blocks=int(data[11])	#* Blocks count *#
        self.dir_block = []
        self.indir_block=[]

        if(data[2]!='s'):#!=symbolic link
            self.dir_block=data[12:24]
            self.indir_block=data[24:27]

class indirect:
    def __init__(self,data):
        self.node_num = int(data[1])
        self.level_indirection  = int(data[2])
        self.logical_offset = int(data[3])
        self.block_indirect = int(data[4])
        self.block_referenced = int(data[5])
def main():
    fail=False
    try:
        read_data=open(sys.argv[1],'r')
    except IOError:
        print("Cannot open input file")
        exit(1)   
    csv_data=csv.reader(read_data)
    for data in csv_data:
        if(data[0]=="SUPERBLOCK"):
            superBlock=Super(data)
        elif data[0]=="GROUP":
            group=Group(data)
        elif data[0]=="IFREE":
            ifree.append(int(data[1]))
        elif data[0]=="BFREE":
            bfree.append(data[1])
        elif data[0]=="INODE":
            inodes.append(Inode(data))
        elif data[0]=="INDIRECT":
            in_dirs.append(indirect(data))
#invliad block
#logical offset for INDIRECT :12
            #DOUBLE INDIRECT :12+256
            #TRIPLE INDIRECT :12+256+256^2

#print(group.inode_table)
    legal_block=int(group.inode_table) + int((superBlock.inode_size*group.inodes_count)/superBlock.bsize)

    dup_blocks={}#keep track of how many time a block is being used


    referenced={}
    allocated=set()
    # for node in inodes:
    #     if(node.node_num!=0):
    #         allocated.add(node.node_num)
    for node in inodes:
        if node.node_num==0:#nothing inside skip it
            continue
        allocated.add(node.node_num)
        #check for dir node
        for block in node.dir_block:
            if int(block)==0:
                continue
            #invalid blocks
            if(int(block)<0 or int(block) > superBlock.blocks_count):
                fail=True
                print("INVALID BLOCK",block,"IN INODE",node.node_num,"AT OFFSET",0)
            #reserved block
            if(int(block)>0 and int(block)<legal_block):
                fail=True
                print("RESERVED BLOCK",block,"IN INODE",node.node_num,"AT OFFSET",0)
            if(block in bfree):
                fail=True
                print("ALLOCATED BLOCK", block, "ON FREELIST")

            if(block not in dup_blocks):
                dup_blocks[block]=[1,node.node_num,"BLOCK",0]
            else:
                print("DUPLICATE BLOCK",block,"IN INODE",node.node_num,"AT OFFSET",0)
                dup_blocks[block][0]+=1
            if(block not in referenced):
                referenced[int(block)]=True


        #single indirect indir_block[0]
        if(int(node.indir_block[0])!=0):
            if(int(node.indir_block[0])<0 or int(node.indir_block[0]) > superBlock.blocks_count):
                fail=True
                print("INVALID INDIRECT BLOCK",node.indir_block[0],"IN INODE",node.node_num,"AT OFFSET",12)
            #reserved block
            if(int(node.indir_block[0])>0 and int(node.indir_block[0])<legal_block):
                fail=True
                print("RESERVED INDIRECT BLOCK",node.indir_block[0],"IN INODE",node.node_num,"AT OFFSET",12)
            if(node.indir_block[0] in bfree):
                fail=True
                print("ALLOCATED BLOCK", node.indir_block[0], "ON FREELIST")

            if(node.indir_block[0] not in dup_blocks):
                dup_blocks[node.indir_block[0]]=[1,node.node_num,"INDIRECT BLOCK",12]
            else:
                print("DUPLICATE INDIRECT BLOCK",node.indir_block[0],"IN INODE",node.node_num,"AT OFFSET",12)
                dup_blocks[node.indir_block[0]][0]+=1

            if(node.indir_block[0] not in referenced):
                referenced[int(node.indir_block[0])]=True

        #double indirect indir_block[1]
        if(int(node.indir_block[1])!=0):
            if(int(node.indir_block[1])<0 or int(node.indir_block[1]) > superBlock.blocks_count):
                fail=True
                print("INVALID DOUBLE INDIRECT BLOCK",node.indir_block[1],"IN INODE",node.node_num,"AT OFFSET",268)
            #reserved block
            if(int(node.indir_block[1])>0 and int(node.indir_block[1])<legal_block):
                fail=True
                print("RESERVED DOUBLE INDIRECT BLOCK",node.indir_block[1],"IN INODE",node.node_num,"AT OFFSET",268)
            if(node.indir_block[1] in bfree):
                fail=True
                print("ALLOCATED BLOCK", node.indir_block[1], "ON FREELIST")
            #dup
            if(node.indir_block[1] not in dup_blocks):
               dup_blocks[node.indir_block[1]]=[1,node.node_num,"DOUBLE INDIRECT BLOCK",268]
            else:
                print("DUPLICATE DOUBLE INDIRECT BLOCK",node.indir_block[1],"IN INODE",node.node_num,"AT OFFSET",268)
                dup_blocks[node.indir_block[1]][0]+=1

            if(node.indir_block[1] not in referenced):
                referenced[int(node.indir_block[1])]=True


        #triple indirect indir_block[2]
        if(int(node.indir_block[2])!=0):
            if(int(node.indir_block[2])<0 or int(node.indir_block[2]) > superBlock.blocks_count):
                fail=True
                print("INVALID TRIPLE INDIRECT BLOCK",node.indir_block[2],"IN INODE",node.node_num,"AT OFFSET",65804)
            #reserved block
            if(int(node.indir_block[2])>0 and int(node.indir_block[2])<legal_block):
                fail=True
                print("RESERVED TRIPLE INDIRECT BLOCK",node.indir_block[2],"IN INODE",node.node_num,"AT OFFSET",65804)
            if(node.indir_block[2] in bfree):
                fail=True
                print("ALLOCATED BLOCK", node.indir_block[2], "ON FREELIST")
               
            if(node.indir_block[2] not in dup_blocks):
                dup_blocks[node.indir_block[2]]=[1,node.node_num,"TRIPLE INDIRECT BLOCK",65804]
            else:
                print("DUPLICATE TRIPLE INDIRECT BLOCK",node.indir_block[2],"IN INODE",node.node_num,"AT OFFSET",65804)
                dup_blocks[node.indir_block[2]][0]+=1

            if(node.indir_block[2] not in referenced):
                referenced[int(node.indir_block[2])]=True
        
    #find DUPLICATE blocks
    for block in dup_blocks:
        if(dup_blocks[block][0]>1):
            fail=True
            print("DUPLICATE",dup_blocks[block][2],block,"IN INODE",dup_blocks[block][1],"AT OFFSET",dup_blocks[block][3])
    

    for each in in_dirs:
        referenced[int(each.block_referenced)]=True
    #check unreferenced blocks
    for block in range(legal_block,superBlock.blocks_count):
        if(int(block) not in referenced) and (str(block) not in bfree):
            fail=True
            print ("UNREFERENCED BLOCK",block )


#check node allocation:
    for node in allocated:
        if node in ifree:
            print("ALLOCATED INODE", node, "ON FREELIST")
    
    #unallocation
    for i in range(superBlock.first_ino,superBlock.inodes_count):
        if(i not in ifree and i not in allocated):
            fail=True           
            print("UNALLOCATED INODE", i, "NOT ON FREELIST")






    if(fail):
        sys.exit(2)
    sys.exit(0)
if __name__ == '__main__':
    main()