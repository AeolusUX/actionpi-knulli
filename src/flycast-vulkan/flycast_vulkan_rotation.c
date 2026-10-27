/* Scoped Action Pi Flycast loader. Rotate the final Vulkan swapchain composition,
 * including all menus. Never replaces the system Vulkan loader.
 * Logical images are 960x720; the real display/swapchain remains 720x960.
 */
#define _GNU_SOURCE
#define VK_NO_PROTOTYPES
#include <vulkan/vulkan.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "flycast_rotation_spv.h"
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetInstanceProcAddr(VkInstance,const char*);
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(VkDevice,const char*);
#define MAX_IMAGES 8
static PFN_vkGetInstanceProcAddr gi;
static PFN_vkGetDeviceProcAddr gd;
static VkInstance inst;
static VkPhysicalDevice phys;
static VkDevice dev;
static uint32_t family;
static VkQueue compose_queue;
static VkPhysicalDeviceMemoryProperties memprops;
#define DECL(n) static PFN_##n r_##n
DECL(vkCreateSwapchainKHR);DECL(vkDestroySwapchainKHR);DECL(vkGetSwapchainImagesKHR);DECL(vkQueuePresentKHR);
DECL(vkCreateImage);DECL(vkDestroyImage);DECL(vkGetImageMemoryRequirements);DECL(vkAllocateMemory);DECL(vkFreeMemory);DECL(vkBindImageMemory);
DECL(vkCreateImageView);DECL(vkDestroyImageView);DECL(vkCreateSampler);DECL(vkDestroySampler);
DECL(vkCreateRenderPass);DECL(vkDestroyRenderPass);DECL(vkCreateFramebuffer);DECL(vkDestroyFramebuffer);
DECL(vkCreateDescriptorSetLayout);DECL(vkDestroyDescriptorSetLayout);DECL(vkCreateDescriptorPool);DECL(vkDestroyDescriptorPool);DECL(vkAllocateDescriptorSets);DECL(vkUpdateDescriptorSets);
DECL(vkCreatePipelineLayout);DECL(vkDestroyPipelineLayout);DECL(vkCreateShaderModule);DECL(vkDestroyShaderModule);DECL(vkCreateGraphicsPipelines);DECL(vkDestroyPipeline);
DECL(vkCreateCommandPool);DECL(vkDestroyCommandPool);DECL(vkAllocateCommandBuffers);DECL(vkResetCommandBuffer);DECL(vkBeginCommandBuffer);DECL(vkEndCommandBuffer);
DECL(vkCmdPipelineBarrier);DECL(vkCmdBeginRenderPass);DECL(vkCmdEndRenderPass);DECL(vkCmdBindPipeline);DECL(vkCmdBindDescriptorSets);DECL(vkCmdDraw);
DECL(vkCreateSemaphore);DECL(vkDestroySemaphore);DECL(vkCreateFence);DECL(vkDestroyFence);DECL(vkWaitForFences);DECL(vkResetFences);DECL(vkQueueSubmit);DECL(vkDeviceWaitIdle);
typedef struct Chain {
 VkSwapchainKHR handle;uint32_t n;
 VkImage real[MAX_IMAGES],image[MAX_IMAGES];VkDeviceMemory memory[MAX_IMAGES];
 VkImageView rv[MAX_IMAGES],iv[MAX_IMAGES];VkFramebuffer fb[MAX_IMAGES];
 VkCommandBuffer cmd[MAX_IMAGES];VkDescriptorSet ds[MAX_IMAGES];VkSemaphore done[MAX_IMAGES];VkFence fence[MAX_IMAGES];
 VkRenderPass pass;VkCommandPool pool;VkPipeline pipeline;VkPipelineLayout layout;
 VkDescriptorSetLayout dsl;VkDescriptorPool dsp;VkSampler sampler;
 struct Chain *next;
} Chain;
static Chain *chains;
static Chain *find(VkSwapchainKHR h){for(Chain*s=chains;s;s=s->next)if(s->handle==h)return s;return NULL;}
static int fake(VkImage im){for(Chain*s=chains;s;s=s->next)for(uint32_t j=0;j<s->n;j++)if(s->image[j]==im)return 1;return 0;}
static void init(void){if(gi)return;void*l=dlopen("/usr/lib/libvulkan.so.1",RTLD_NOW|RTLD_LOCAL|RTLD_DEEPBIND);if(!l){fprintf(stderr,"ACTIONPI_VK_ROT real loader: %s\n",dlerror());return;}gi=dlsym(l,"vkGetInstanceProcAddr");gd=dlsym(l,"vkGetDeviceProcAddr");}
#define LOAD(n) do{r_##n=(PFN_##n)gd(dev,#n);if(!r_##n){fprintf(stderr,"ACTIONPI_VK_ROT missing %s\n",#n);return 0;}}while(0)
static int load_device(void){
 LOAD(vkCreateSwapchainKHR);LOAD(vkDestroySwapchainKHR);LOAD(vkGetSwapchainImagesKHR);LOAD(vkQueuePresentKHR);
 LOAD(vkCreateImage);LOAD(vkDestroyImage);LOAD(vkGetImageMemoryRequirements);LOAD(vkAllocateMemory);LOAD(vkFreeMemory);LOAD(vkBindImageMemory);
 LOAD(vkCreateImageView);LOAD(vkDestroyImageView);LOAD(vkCreateSampler);LOAD(vkDestroySampler);
 LOAD(vkCreateRenderPass);LOAD(vkDestroyRenderPass);LOAD(vkCreateFramebuffer);LOAD(vkDestroyFramebuffer);
 LOAD(vkCreateDescriptorSetLayout);LOAD(vkDestroyDescriptorSetLayout);LOAD(vkCreateDescriptorPool);LOAD(vkDestroyDescriptorPool);LOAD(vkAllocateDescriptorSets);LOAD(vkUpdateDescriptorSets);
 LOAD(vkCreatePipelineLayout);LOAD(vkDestroyPipelineLayout);LOAD(vkCreateShaderModule);LOAD(vkDestroyShaderModule);LOAD(vkCreateGraphicsPipelines);LOAD(vkDestroyPipeline);
 LOAD(vkCreateCommandPool);LOAD(vkDestroyCommandPool);LOAD(vkAllocateCommandBuffers);LOAD(vkResetCommandBuffer);LOAD(vkBeginCommandBuffer);LOAD(vkEndCommandBuffer);
 LOAD(vkCmdPipelineBarrier);LOAD(vkCmdBeginRenderPass);LOAD(vkCmdEndRenderPass);LOAD(vkCmdBindPipeline);LOAD(vkCmdBindDescriptorSets);LOAD(vkCmdDraw);
 LOAD(vkCreateSemaphore);LOAD(vkDestroySemaphore);LOAD(vkCreateFence);LOAD(vkDestroyFence);LOAD(vkWaitForFences);LOAD(vkResetFences);LOAD(vkQueueSubmit);LOAD(vkDeviceWaitIdle);
 return 1;
}
static void cleanup(Chain*s){
 if(!s)return;
 for(uint32_t i=0;i<s->n;i++){
  if(s->fence[i])r_vkDestroyFence(dev,s->fence[i],NULL);
  if(s->done[i])r_vkDestroySemaphore(dev,s->done[i],NULL);
  if(s->fb[i])r_vkDestroyFramebuffer(dev,s->fb[i],NULL);
  if(s->rv[i])r_vkDestroyImageView(dev,s->rv[i],NULL);
  if(s->iv[i])r_vkDestroyImageView(dev,s->iv[i],NULL);
  if(s->image[i])r_vkDestroyImage(dev,s->image[i],NULL);
  if(s->memory[i])r_vkFreeMemory(dev,s->memory[i],NULL);
 }
 if(s->pool)r_vkDestroyCommandPool(dev,s->pool,NULL);
 if(s->pipeline)r_vkDestroyPipeline(dev,s->pipeline,NULL);
 if(s->layout)r_vkDestroyPipelineLayout(dev,s->layout,NULL);
 if(s->dsp)r_vkDestroyDescriptorPool(dev,s->dsp,NULL);
 if(s->dsl)r_vkDestroyDescriptorSetLayout(dev,s->dsl,NULL);
 if(s->sampler)r_vkDestroySampler(dev,s->sampler,NULL);
 if(s->pass)r_vkDestroyRenderPass(dev,s->pass,NULL);
 free(s);
}
#define TRY(call) do{VkResult rr=(call);if(rr!=VK_SUCCESS){fprintf(stderr,"ACTIONPI_VK_ROT %s: %d\n",#call,rr);return rr;}}while(0)
static VkResult resources(Chain*s,VkFormat format){
 VkAttachmentDescription a={.format=format,.samples=VK_SAMPLE_COUNT_1_BIT,.loadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE,.storeOp=VK_ATTACHMENT_STORE_OP_STORE,.stencilLoadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE,.stencilStoreOp=VK_ATTACHMENT_STORE_OP_DONT_CARE,.initialLayout=VK_IMAGE_LAYOUT_UNDEFINED,.finalLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR};
 VkAttachmentReference ar={0,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL};VkSubpassDescription sub={.pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,.colorAttachmentCount=1,.pColorAttachments=&ar};
 VkRenderPassCreateInfo rp={.sType=VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,.attachmentCount=1,.pAttachments=&a,.subpassCount=1,.pSubpasses=&sub};TRY(r_vkCreateRenderPass(dev,&rp,NULL,&s->pass));
 VkSamplerCreateInfo sp={.sType=VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO,.magFilter=VK_FILTER_NEAREST,.minFilter=VK_FILTER_NEAREST,.mipmapMode=VK_SAMPLER_MIPMAP_MODE_NEAREST,.addressModeU=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE,.addressModeV=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE,.addressModeW=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE,.maxLod=0};TRY(r_vkCreateSampler(dev,&sp,NULL,&s->sampler));
 VkDescriptorSetLayoutBinding binding={.binding=0,.descriptorType=VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,.descriptorCount=1,.stageFlags=VK_SHADER_STAGE_FRAGMENT_BIT};
 VkDescriptorSetLayoutCreateInfo dsl={.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,.bindingCount=1,.pBindings=&binding};TRY(r_vkCreateDescriptorSetLayout(dev,&dsl,NULL,&s->dsl));
 VkDescriptorPoolSize ps={VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,s->n};VkDescriptorPoolCreateInfo dp={.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,.maxSets=s->n,.poolSizeCount=1,.pPoolSizes=&ps};TRY(r_vkCreateDescriptorPool(dev,&dp,NULL,&s->dsp));
 VkPipelineLayoutCreateInfo pl={.sType=VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,.setLayoutCount=1,.pSetLayouts=&s->dsl};TRY(r_vkCreatePipelineLayout(dev,&pl,NULL,&s->layout));
 VkShaderModule shaders[2]={0};VkShaderModuleCreateInfo sm={.sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,.codeSize=sizeof(rotation_vert),.pCode=rotation_vert};
 TRY(r_vkCreateShaderModule(dev,&sm,NULL,&shaders[0]));sm.codeSize=sizeof(rotation_frag);sm.pCode=rotation_frag;
 VkResult sr=r_vkCreateShaderModule(dev,&sm,NULL,&shaders[1]);if(sr!=VK_SUCCESS){r_vkDestroyShaderModule(dev,shaders[0],NULL);return sr;}
 VkPipelineShaderStageCreateInfo stages[2]={{.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,.stage=VK_SHADER_STAGE_VERTEX_BIT,.module=shaders[0],.pName="main"},{.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,.stage=VK_SHADER_STAGE_FRAGMENT_BIT,.module=shaders[1],.pName="main"}};
 VkPipelineVertexInputStateCreateInfo vi={.sType=VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};VkPipelineInputAssemblyStateCreateInfo ia={.sType=VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,.topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST};
 VkViewport vp={0,0,720,960,0,1};VkRect2D sc={{0,0},{720,960}};VkPipelineViewportStateCreateInfo vs={.sType=VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,.viewportCount=1,.pViewports=&vp,.scissorCount=1,.pScissors=&sc};
 VkPipelineRasterizationStateCreateInfo rs={.sType=VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,.polygonMode=VK_POLYGON_MODE_FILL,.cullMode=VK_CULL_MODE_NONE,.frontFace=VK_FRONT_FACE_COUNTER_CLOCKWISE,.lineWidth=1};
 VkPipelineMultisampleStateCreateInfo ms={.sType=VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,.rasterizationSamples=VK_SAMPLE_COUNT_1_BIT};
 VkPipelineColorBlendAttachmentState ba={.colorWriteMask=15};VkPipelineColorBlendStateCreateInfo bs={.sType=VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,.attachmentCount=1,.pAttachments=&ba};
 VkGraphicsPipelineCreateInfo gp={.sType=VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,.stageCount=2,.pStages=stages,.pVertexInputState=&vi,.pInputAssemblyState=&ia,.pViewportState=&vs,.pRasterizationState=&rs,.pMultisampleState=&ms,.pColorBlendState=&bs,.layout=s->layout,.renderPass=s->pass};
 sr=r_vkCreateGraphicsPipelines(dev,VK_NULL_HANDLE,1,&gp,NULL,&s->pipeline);r_vkDestroyShaderModule(dev,shaders[0],NULL);r_vkDestroyShaderModule(dev,shaders[1],NULL);TRY(sr);
 VkCommandPoolCreateInfo cp={.sType=VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,.queueFamilyIndex=family};TRY(r_vkCreateCommandPool(dev,&cp,NULL,&s->pool));
 VkCommandBufferAllocateInfo ca={.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,.commandPool=s->pool,.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY,.commandBufferCount=s->n};TRY(r_vkAllocateCommandBuffers(dev,&ca,s->cmd));
 for(uint32_t i=0;i<s->n;i++){
  VkImageCreateInfo im={.sType=VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,.imageType=VK_IMAGE_TYPE_2D,.format=format,.extent={960,720,1},.mipLevels=1,.arrayLayers=1,.samples=VK_SAMPLE_COUNT_1_BIT,.tiling=VK_IMAGE_TILING_OPTIMAL,.usage=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT,.sharingMode=VK_SHARING_MODE_EXCLUSIVE,.initialLayout=VK_IMAGE_LAYOUT_UNDEFINED};TRY(r_vkCreateImage(dev,&im,NULL,&s->image[i]));
  VkMemoryRequirements mr;r_vkGetImageMemoryRequirements(dev,s->image[i],&mr);uint32_t mt=UINT32_MAX;
  for(uint32_t j=0;j<memprops.memoryTypeCount;j++)if((mr.memoryTypeBits&(1u<<j))&&(memprops.memoryTypes[j].propertyFlags&VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)){mt=j;break;}
  if(mt==UINT32_MAX)return VK_ERROR_FEATURE_NOT_PRESENT;
  VkMemoryAllocateInfo ma={.sType=VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,.allocationSize=mr.size,.memoryTypeIndex=mt};TRY(r_vkAllocateMemory(dev,&ma,NULL,&s->memory[i]));TRY(r_vkBindImageMemory(dev,s->image[i],s->memory[i],0));
  VkImageViewCreateInfo iv={.sType=VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,.image=s->image[i],.viewType=VK_IMAGE_VIEW_TYPE_2D,.format=format,.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1}};TRY(r_vkCreateImageView(dev,&iv,NULL,&s->iv[i]));iv.image=s->real[i];TRY(r_vkCreateImageView(dev,&iv,NULL,&s->rv[i]));
  VkFramebufferCreateInfo fb={.sType=VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,.renderPass=s->pass,.attachmentCount=1,.pAttachments=&s->rv[i],.width=720,.height=960,.layers=1};TRY(r_vkCreateFramebuffer(dev,&fb,NULL,&s->fb[i]));
  VkDescriptorSetAllocateInfo da={.sType=VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,.descriptorPool=s->dsp,.descriptorSetCount=1,.pSetLayouts=&s->dsl};TRY(r_vkAllocateDescriptorSets(dev,&da,&s->ds[i]));
  VkDescriptorImageInfo di={s->sampler,s->iv[i],VK_IMAGE_LAYOUT_GENERAL};VkWriteDescriptorSet wr={.sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,.dstSet=s->ds[i],.dstBinding=0,.descriptorCount=1,.descriptorType=VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,.pImageInfo=&di};r_vkUpdateDescriptorSets(dev,1,&wr,0,NULL);
  VkSemaphoreCreateInfo se={.sType=VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO};TRY(r_vkCreateSemaphore(dev,&se,NULL,&s->done[i]));VkFenceCreateInfo fe={.sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO,.flags=VK_FENCE_CREATE_SIGNALED_BIT};TRY(r_vkCreateFence(dev,&fe,NULL,&s->fence[i]));
 }
 return VK_SUCCESS;
}
VKAPI_ATTR VkResult VKAPI_CALL vkCreateInstance(const VkInstanceCreateInfo*a,const VkAllocationCallbacks*b,VkInstance*c){init();if(!gi)return VK_ERROR_INITIALIZATION_FAILED;PFN_vkCreateInstance f=(void*)gi(NULL,"vkCreateInstance");VkResult r=f(a,b,c);if(r==VK_SUCCESS)inst=*c;return r;}
VKAPI_ATTR VkResult VKAPI_CALL vkCreateDevice(VkPhysicalDevice p,const VkDeviceCreateInfo*a,const VkAllocationCallbacks*b,VkDevice*c){
 PFN_vkCreateDevice f=(void*)gi(inst,"vkCreateDevice");VkResult r=f(p,a,b,c);if(r!=VK_SUCCESS)return r;phys=p;dev=*c;
 PFN_vkGetPhysicalDeviceQueueFamilyProperties q=(void*)gi(inst,"vkGetPhysicalDeviceQueueFamilyProperties");uint32_t n=0;q(p,&n,NULL);VkQueueFamilyProperties*props=calloc(n,sizeof(*props));if(!props)return VK_ERROR_OUT_OF_HOST_MEMORY;q(p,&n,props);family=UINT32_MAX;
 for(uint32_t i=0;i<a->queueCreateInfoCount;i++){uint32_t j=a->pQueueCreateInfos[i].queueFamilyIndex;if(j<n&&(props[j].queueFlags&VK_QUEUE_GRAPHICS_BIT)){family=j;break;}}free(props);
 PFN_vkGetPhysicalDeviceMemoryProperties m=(void*)gi(inst,"vkGetPhysicalDeviceMemoryProperties");m(p,&memprops);PFN_vkGetDeviceQueue g=(void*)gd(dev,"vkGetDeviceQueue");if(family!=UINT32_MAX)g(dev,family,0,&compose_queue);
 return r;
}
VKAPI_ATTR VkResult VKAPI_CALL vkGetDisplayModePropertiesKHR(VkPhysicalDevice p,VkDisplayKHR d,uint32_t*n,VkDisplayModePropertiesKHR*out){PFN_vkGetDisplayModePropertiesKHR f=(void*)gi(inst,"vkGetDisplayModePropertiesKHR");VkResult r=f(p,d,n,out);if(r>=0&&out)for(uint32_t i=0;i<*n;i++)if(out[i].parameters.visibleRegion.width==720&&out[i].parameters.visibleRegion.height==960)out[i].parameters.visibleRegion=(VkExtent2D){960,720};return r;}
VKAPI_ATTR VkResult VKAPI_CALL vkCreateDisplayPlaneSurfaceKHR(VkInstance i,const VkDisplaySurfaceCreateInfoKHR*a,const VkAllocationCallbacks*b,VkSurfaceKHR*c){PFN_vkCreateDisplayPlaneSurfaceKHR f=(void*)gi(i,"vkCreateDisplayPlaneSurfaceKHR");VkDisplaySurfaceCreateInfoKHR v=*a;if(v.imageExtent.width==960&&v.imageExtent.height==720)v.imageExtent=(VkExtent2D){720,960};return f(i,&v,b,c);}
VKAPI_ATTR VkResult VKAPI_CALL vkGetPhysicalDeviceSurfaceCapabilitiesKHR(VkPhysicalDevice p,VkSurfaceKHR s,VkSurfaceCapabilitiesKHR*out){PFN_vkGetPhysicalDeviceSurfaceCapabilitiesKHR f=(void*)gi(inst,"vkGetPhysicalDeviceSurfaceCapabilitiesKHR");VkResult r=f(p,s,out);if(r==VK_SUCCESS&&out->currentExtent.width==720&&out->currentExtent.height==960){out->currentExtent=(VkExtent2D){960,720};out->minImageExtent=(VkExtent2D){out->minImageExtent.height,out->minImageExtent.width};out->maxImageExtent=(VkExtent2D){out->maxImageExtent.height,out->maxImageExtent.width};}return r;}
VKAPI_ATTR VkResult VKAPI_CALL vkCreateSwapchainKHR(VkDevice d,const VkSwapchainCreateInfoKHR*a,const VkAllocationCallbacks*b,VkSwapchainKHR*out){
 dev=d;if(!load_device()||family==UINT32_MAX)return VK_ERROR_INITIALIZATION_FAILED;
 if(a->imageExtent.width!=960||a->imageExtent.height!=720)return r_vkCreateSwapchainKHR(d,a,b,out);
 if(a->imageArrayLayers!=1)return VK_ERROR_FEATURE_NOT_PRESENT;
 VkSwapchainCreateInfoKHR v=*a;v.imageExtent=(VkExtent2D){720,960};v.imageUsage|=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;TRY(r_vkCreateSwapchainKHR(d,&v,b,out));
 Chain*s=calloc(1,sizeof(*s));if(!s){r_vkDestroySwapchainKHR(d,*out,b);return VK_ERROR_OUT_OF_HOST_MEMORY;}s->handle=*out;
 VkResult r=r_vkGetSwapchainImagesKHR(d,*out,&s->n,NULL);if(r!=VK_SUCCESS||s->n>MAX_IMAGES){s->n=0;cleanup(s);r_vkDestroySwapchainKHR(d,*out,b);return VK_ERROR_INITIALIZATION_FAILED;}
 r=r_vkGetSwapchainImagesKHR(d,*out,&s->n,s->real);if(r==VK_SUCCESS)r=resources(s,a->imageFormat);
 if(r!=VK_SUCCESS){cleanup(s);r_vkDestroySwapchainKHR(d,*out,b);return r;}
 s->next=chains;chains=s;fprintf(stderr,"ACTIONPI_VK_ROT logical=960x720 physical=720x960 clockwise90 images=%u\n",s->n);return VK_SUCCESS;
}
VKAPI_ATTR VkResult VKAPI_CALL vkGetSwapchainImagesKHR(VkDevice d,VkSwapchainKHR h,uint32_t*n,VkImage*out){Chain*s=find(h);if(!s)return r_vkGetSwapchainImagesKHR(d,h,n,out);if(!out){*n=s->n;return VK_SUCCESS;}uint32_t c=*n<s->n?*n:s->n;memcpy(out,s->image,c*sizeof(*out));*n=c;return c<s->n?VK_INCOMPLETE:VK_SUCCESS;}
VKAPI_ATTR void VKAPI_CALL vkDestroySwapchainKHR(VkDevice d,VkSwapchainKHR h,const VkAllocationCallbacks*a){Chain**p=&chains;while(*p&&(*p)->handle!=h)p=&(*p)->next;if(*p){r_vkDeviceWaitIdle(d);Chain*s=*p;*p=s->next;cleanup(s);}r_vkDestroySwapchainKHR(d,h,a);}
VKAPI_ATTR VkResult VKAPI_CALL vkCreateRenderPass(VkDevice d,const VkRenderPassCreateInfo*a,const VkAllocationCallbacks*b,VkRenderPass*out){
 if(!r_vkCreateRenderPass)r_vkCreateRenderPass=(void*)gd(d,"vkCreateRenderPass");VkRenderPassCreateInfo v=*a;VkAttachmentDescription*at=NULL;
 if(a->attachmentCount){at=malloc(a->attachmentCount*sizeof(*at));if(!at)return VK_ERROR_OUT_OF_HOST_MEMORY;memcpy(at,a->pAttachments,a->attachmentCount*sizeof(*at));for(uint32_t i=0;i<a->attachmentCount;i++){if(at[i].initialLayout==VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)at[i].initialLayout=VK_IMAGE_LAYOUT_GENERAL;if(at[i].finalLayout==VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)at[i].finalLayout=VK_IMAGE_LAYOUT_GENERAL;}v.pAttachments=at;}
 VkResult r=r_vkCreateRenderPass(d,&v,b,out);free(at);return r;
}
VKAPI_ATTR void VKAPI_CALL vkCmdPipelineBarrier(VkCommandBuffer c,VkPipelineStageFlags src,VkPipelineStageFlags dst,VkDependencyFlags dep,uint32_t mc,const VkMemoryBarrier*m,uint32_t bc,const VkBufferMemoryBarrier*b,uint32_t ic,const VkImageMemoryBarrier*i){
 if(!r_vkCmdPipelineBarrier)r_vkCmdPipelineBarrier=(void*)gd(dev,"vkCmdPipelineBarrier");
 VkImageMemoryBarrier*copy=NULL;if(ic){copy=malloc(ic*sizeof(*copy));if(!copy){fprintf(stderr,"ACTIONPI_VK_ROT barrier allocation failed\n");abort();}memcpy(copy,i,ic*sizeof(*copy));for(uint32_t j=0;j<ic;j++)if(fake(copy[j].image)){if(copy[j].oldLayout==VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)copy[j].oldLayout=VK_IMAGE_LAYOUT_GENERAL;if(copy[j].newLayout==VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)copy[j].newLayout=VK_IMAGE_LAYOUT_GENERAL;}}
 r_vkCmdPipelineBarrier(c,src,dst,dep,mc,m,bc,b,ic,copy?copy:i);free(copy);
}
VKAPI_ATTR VkResult VKAPI_CALL vkQueuePresentKHR(VkQueue q,const VkPresentInfoKHR*a){
 if(a->swapchainCount!=1)return r_vkQueuePresentKHR(q,a);Chain*s=find(a->pSwapchains[0]);if(!s)return r_vkQueuePresentKHR(q,a);uint32_t i=a->pImageIndices[0];if(i>=s->n)return VK_ERROR_INITIALIZATION_FAILED;
 TRY(r_vkWaitForFences(dev,1,&s->fence[i],VK_TRUE,UINT64_MAX));TRY(r_vkResetFences(dev,1,&s->fence[i]));TRY(r_vkResetCommandBuffer(s->cmd[i],0));VkCommandBufferBeginInfo cb={.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,.flags=VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT};TRY(r_vkBeginCommandBuffer(s->cmd[i],&cb));
 VkImageMemoryBarrier bar={.sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,.srcAccessMask=VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT|VK_ACCESS_MEMORY_WRITE_BIT,.dstAccessMask=VK_ACCESS_SHADER_READ_BIT,.oldLayout=VK_IMAGE_LAYOUT_GENERAL,.newLayout=VK_IMAGE_LAYOUT_GENERAL,.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,.image=s->image[i],.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1}};r_vkCmdPipelineBarrier(s->cmd[i],VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT,0,0,NULL,0,NULL,1,&bar);
 VkRenderPassBeginInfo rp={.sType=VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,.renderPass=s->pass,.framebuffer=s->fb[i],.renderArea={{0,0},{720,960}}};r_vkCmdBeginRenderPass(s->cmd[i],&rp,VK_SUBPASS_CONTENTS_INLINE);r_vkCmdBindPipeline(s->cmd[i],VK_PIPELINE_BIND_POINT_GRAPHICS,s->pipeline);r_vkCmdBindDescriptorSets(s->cmd[i],VK_PIPELINE_BIND_POINT_GRAPHICS,s->layout,0,1,&s->ds[i],0,NULL);r_vkCmdDraw(s->cmd[i],3,1,0,0);r_vkCmdEndRenderPass(s->cmd[i]);TRY(r_vkEndCommandBuffer(s->cmd[i]));
 VkPipelineStageFlags*stages=calloc(a->waitSemaphoreCount?a->waitSemaphoreCount:1,sizeof(*stages));if(!stages)return VK_ERROR_OUT_OF_HOST_MEMORY;for(uint32_t j=0;j<a->waitSemaphoreCount;j++)stages[j]=VK_PIPELINE_STAGE_ALL_COMMANDS_BIT;
 VkSubmitInfo si={.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO,.waitSemaphoreCount=a->waitSemaphoreCount,.pWaitSemaphores=a->pWaitSemaphores,.pWaitDstStageMask=stages,.commandBufferCount=1,.pCommandBuffers=&s->cmd[i],.signalSemaphoreCount=1,.pSignalSemaphores=&s->done[i]};VkResult r=r_vkQueueSubmit(compose_queue,1,&si,s->fence[i]);free(stages);if(r!=VK_SUCCESS)return r;
 VkPresentInfoKHR p=*a;p.waitSemaphoreCount=1;p.pWaitSemaphores=&s->done[i];return r_vkQueuePresentKHR(q,&p);
}
static PFN_vkVoidFunction replace(const char*n,PFN_vkVoidFunction f){
 if(!f)return NULL;
#define MAP(x) if(!strcmp(n,#x))return(PFN_vkVoidFunction)x
 MAP(vkGetInstanceProcAddr);MAP(vkGetDeviceProcAddr);MAP(vkCreateInstance);MAP(vkCreateDevice);MAP(vkGetDisplayModePropertiesKHR);MAP(vkCreateDisplayPlaneSurfaceKHR);MAP(vkGetPhysicalDeviceSurfaceCapabilitiesKHR);MAP(vkCreateSwapchainKHR);MAP(vkGetSwapchainImagesKHR);MAP(vkDestroySwapchainKHR);MAP(vkCreateRenderPass);MAP(vkCmdPipelineBarrier);MAP(vkQueuePresentKHR);
 return f;
}
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetInstanceProcAddr(VkInstance i,const char*n){init();if(!gi)return NULL;return replace(n,gi(i,n));}
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(VkDevice d,const char*n){init();if(!gd)return NULL;return replace(n,gd(d,n));}
