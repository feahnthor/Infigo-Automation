class Locators:
  """
  Locators using Helium and Selenium which is why most of this are not css identifies
  """
#Locators for login page
  test = 'https://backgroundtown.com/Admin/Product' 
  base_prod_url = 'https://backgroundtown.com/Admin/Product/Edit/2954' #Mark Lane
  #base_prod_url = 'https://backgroundtown.com/Admin/Product/Edit/2605' #Kara KMC
  # base_floor_prod_url = 'https://backgroundtown.com/Admin/Product/Edit/2568' #Mark Lane
  base_floor_prod_url = 'https://backgroundtown.com/Admin/Product/Edit/2606' # Kara KMC
  email = 'Email:'
  password = 'Password:'
  login_button = 'Login'

#Available product page
  product_dropdown = '#ProductVariants option' #use Select class and methods

#Product page
  copy_prod_btn = 'Copy product'
  new_name_for_copy = '#CopyProductModel_Name' # this is an input and needs to have values replaced
  new_prod_name = 'New product name'
  save_and_continue = 'Save and Continue Edit'
  copy_data_checkbox = '#CopyProductModel_CopyCatfishRelated'
  copy_extended_checkbox = 'Copy extended data'
  copy_images_checkbox = 'Copy Images'
  copy_window = 'copyproduct-window'
  product_edit_tabs = 'product-edit' #ID for tabs on main page. I.e. Pictures, SEO, Category Mappings
  # confirm_copy = '#copyproduct-window  button.button.t-state-default'

  picture_tab = 'Pictures'
  prod_info_tab = 'Product Info'
  upload = 'Upload a file'
  add_picture = 'Add product picture'
# Product Page -> Product Info tab Add Tags
  first_tag = 'ACI Collection'
  published = 'Published'
  show_in_search = 'Show in Search Result'

# Add Categories
  category = 'Category mappings'
  add_record = 'Add new record'
  first = 'Styles'
  floor = 'RubberMat Flooring >> '
  backdrop = 'Backdrop >> '
  designer_category = 'Designer >> '
  theme_category = 'Themes >> '
  color_category = 'Color >> '
  selected_category = '#productcategories-gridform span.t-input'
  back_to_variants = '(back to product variant details)'
                      
  
  variants = 'Product variants'
  unnamed = 'Unnamed'
  edit = 'Edit'
  size_key = 'size'
  images = 'Images'
  delete = 'Delete'

  tag_field = 'Product tags:'
  tag_class = 'tagItem'
  tag_add_text = 'manualTagText'
  tag_window = 'tagEditor'

#Variants
  update = 'Update'

  delete_logic = 'deleteAttrCondition'
  size_logic = '.eAttributeContainer'
  logic_fields = 'level-item'
  top_of_variant_page = 'productvariant-form'

  attribute_logic_list_id = '#priceEngContainer li'
  attribute_edit = 'View/Edit value (Total:'
  attribute_label_1 = 'Size'
  attribute_label_2 = 'Mentor'
  attribute_label_canvas = 'Canvas'
  variant_price_adjustment = 'Price adjustment:'
  code_name = 'Name:'
  code_f_name = 'Friendly Name:'
  price = 'Price adjustment:'

  tabs = '#product-edit ul li' #tabs include 'Product Info', 'Category Mapping'
  designer = '#product-edit-4 #productcategories-grid tbody tr td'
  attribute = 'Attributes'
  popup_esc_tab = 'General'

## Variant Size
  var_delete_btn = '#pvav-grid tbody tr td:nth-of-type(11)'
  variant_name = '#pvav-grid tbody tr td:nth-of-type(1)' # cannot be a value of 0
  var_row_selector = '#pvav-grid tbody tr'


  attribute_combinations = '#attributecombinations-grid tbody tr'
## New Combination window
  image_tab = '#productattributecombination-edit li' # use index 1


 
  #Specification

  spec_attribute = '#product-edit-8 #specificationattributes-grid tbody tr td'
  hide_checkbox = 'Add`SpecificationAttributeModel_HideFromCustomer'
  spec_add_button = '#product-edit-8 .adminContent button#addProductSpec'

  variant_wait = '#product-variants tbody tr td.t-last'
  variant_btn = '#product-variants tbody tr td.t-last a.button'

#Variant Page
  v_wait = '#productvariant-edit ul li'
  sku = 'sku'
  v_tabs = '#productvariant-edit ul li a'

